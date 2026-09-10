// Sulu Mangrove Dynamics GeoAI
// Export the complete 19-municipality Sulu CGMD stack, 1995-2023,
// aligned to the GMW v4.1.12 grid.

var adm3 = ee.FeatureCollection(
  'projects/earthengine-legacy/assets/projects/sat-io/open-datasets/geoboundaries/SSCU-ADM3'
);

var muniNames = ee.List([
  'Indanan','Jolo','Kalingalan Caluang','Luuk','Maimbung',
  'Hadji Panglima Tahil','Old Panamao','Pangutaran','Parang','Pata',
  'Patikul','Siasi','Talipao','Tapul','Tongkil','Panglima Estino',
  'Lugus','Pandami','Omar'
]);

var searchBox = ee.Geometry.Rectangle([119.5, 5.2, 122.2, 6.7], null, false);
var municipalities = adm3
  .filterBounds(searchBox)
  .filter(ee.Filter.inList('shapeName', muniNames));

print('Municipality count - MUST BE 19:', municipalities.size());
print('Municipality names:', municipalities.aggregate_array('shapeName').sort());

var suluGeom = municipalities.geometry();
var exportBounds = suluGeom.bounds();
Map.centerObject(municipalities, 8);
Map.addLayer(municipalities.style({color:'FF0000', fillColor:'00000000', width:1}), {}, '19 Sulu Municipalities', true);

var cgmd = ee.FeatureCollection('projects/mangrovedatahub2/assets/CGMD-Extent30');
var cgmdSulu = cgmd
  .filterBounds(exportBounds)
  .filter(ee.Filter.gte('year', 1995))
  .filter(ee.Filter.lte('year', 2023));

var years = ee.List.sequence(1995, 2023);
var bandNames = years.map(function(y) {
  return ee.String('m').cat(ee.Number(y).format('%d'));
});

var annualImages = years.map(function(y) {
  y = ee.Number(y);
  var annual = cgmdSulu.filter(ee.Filter.eq('year', y));
  return ee.Image(0).byte().paint(annual, 1)
    .rename(ee.String('m').cat(y.format('%d')));
});

var stack = ee.ImageCollection.fromImages(annualImages)
  .toBands().rename(bandNames).toByte();

var suluMask = ee.Image(0).byte().paint(municipalities, 1);
var maskedStack = stack.updateMask(suluMask.eq(1));
print('Band count - EXPECTED 29:', maskedStack.bandNames().size());

Map.addLayer(maskedStack.select('m2023').selfMask(), {palette:['006400']}, 'CGMD 2023', true);

// 30-m GMW grid. The 119E origin is on the same 1-degree / 3711-pixel GMW grid.
var gmwTransform = [
  0.00026946914578280785, 0, 119.0,
  0, -0.00026946914578280785, 7.0
];

Export.table.toDrive({
  collection: municipalities,
  description: 'Sulu_Municipal_Boundaries_19_CORRECTED',
  folder: 'Sulu_Mangrove_Research',
  fileNamePrefix: 'Sulu_Municipal_Boundaries_19_CORRECTED',
  fileFormat: 'GeoJSON'
});

Export.image.toDrive({
  image: maskedStack,
  description: 'Sulu_CGMD_1995_2023_19Muni_OPTIMIZED',
  folder: 'Sulu_Mangrove_Research',
  fileNamePrefix: 'Sulu_CGMD_1995_2023_19Muni_OPTIMIZED',
  region: exportBounds,
  crs: 'EPSG:4326',
  crsTransform: gmwTransform,
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF'
});

print('Run exports only if municipality count = 19.');
