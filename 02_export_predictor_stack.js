// Sulu Mangrove Dynamics GeoAI
// Environmental and anthropogenic predictor audit stack (~90 m).
// The primary Python model retains only the eight predictors documented in CODEBOOK.md.

var adm3 = ee.FeatureCollection(
  'projects/earthengine-legacy/assets/projects/sat-io/open-datasets/geoboundaries/SSCU-ADM3'
);
var muniNames = ee.List([
  'Indanan','Jolo','Kalingalan Caluang','Luuk','Maimbung',
  'Hadji Panglima Tahil','Old Panamao','Pangutaran','Parang','Pata',
  'Patikul','Siasi','Talipao','Tapul','Tongkil','Panglima Estino',
  'Lugus','Pandami','Omar'
]);
var searchBox = ee.Geometry.Rectangle([119.5,5.2,122.2,6.7], null, false);
var municipalities = adm3.filterBounds(searchBox)
  .filter(ee.Filter.inList('shapeName', muniNames));
print('Municipality count - MUST BE 19:', municipalities.size());
var region = municipalities.geometry();
var exportBounds = region.bounds();
Map.centerObject(municipalities, 8);

var demRaw = ee.Image('NASA/NASADEM_HGT/001').select('elevation');
var elevation = demRaw.rename('elevation_m');
var slope = ee.Terrain.slope(demRaw).rename('slope_deg');

var gsw = ee.Image('JRC/GSW1_4/GlobalSurfaceWater');
var waterOccurrence = gsw.select('occurrence').unmask(0).rename('water_occurrence_pct');
var waterSeasonality = gsw.select('seasonality').unmask(0).rename('water_seasonality_months');
var waterRecurrence = gsw.select('recurrence').unmask(0).rename('water_recurrence_pct');
var waterChange = gsw.select('change_abs').unmask(0).rename('water_change_abs_pct');
var waterMaxExtent = gsw.select('max_extent').unmask(0).rename('water_max_extent');

var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').select('precipitation');
var climateYears = ee.List.sequence(1995, 2023);
var annualRain = ee.ImageCollection.fromImages(climateYears.map(function(y) {
  y = ee.Number(y);
  var start = ee.Date.fromYMD(y,1,1);
  var end = start.advance(1,'year');
  var annual = chirps.filterDate(start,end).sum().rename('annual_precip_mm');
  return ee.Image.constant(y).float().rename('year').addBands(annual)
    .set('system:time_start', start.millis());
}));
var rainfallMean = annualRain.select('annual_precip_mm').mean().rename('rain_mean_annual_mm');
var rainfallSD = annualRain.select('annual_precip_mm').reduce(ee.Reducer.stdDev());
var rainfallCV = rainfallSD.divide(rainfallMean).multiply(100).rename('rain_interannual_cv_pct');
var rainfallTrend = annualRain.select(['year','annual_precip_mm'])
  .reduce(ee.Reducer.linearFit()).select('scale').rename('rain_trend_mm_per_year');

var built2000 = ee.Image('JRC/GHSL/P2023A/GHS_BUILT_S/2000').select('built_surface')
  .divide(10000).rename('built_fraction_2000');
var built2020 = ee.Image('JRC/GHSL/P2023A/GHS_BUILT_S/2020').select('built_surface')
  .divide(10000).rename('built_fraction_2020');
var builtChange = built2020.subtract(built2000).rename('built_fraction_change_2000_2020');

var worldPop = ee.ImageCollection('WorldPop/GP/100m/pop').filter(ee.Filter.eq('country','PHL'));
var pop2000Raw = worldPop.filter(ee.Filter.eq('year',2000)).mosaic().select('population');
var pop2020Raw = worldPop.filter(ee.Filter.eq('year',2020)).mosaic().select('population');
var popDensity2000 = pop2000Raw.divide(ee.Image.pixelArea()).multiply(1e6).rename('population_density_2000');
var popDensity2020 = pop2020Raw.divide(ee.Image.pixelArea()).multiply(1e6).rename('population_density_2020');
var populationChange = popDensity2020.subtract(popDensity2000).rename('population_density_change_2000_2020');

var predictors = ee.Image.cat([
  elevation, slope,
  waterOccurrence, waterSeasonality, waterRecurrence, waterChange, waterMaxExtent,
  rainfallMean, rainfallCV, rainfallTrend,
  built2000, built2020, builtChange,
  popDensity2000, popDensity2020, populationChange
]).float();

print('Predictor bands - EXPECTED 16:', predictors.bandNames());
var suluMask = ee.Image(0).byte().paint(municipalities, 1);
predictors = predictors.updateMask(suluMask.eq(1));

var res90 = 0.00026946914578280785 * 3;
var transform90 = [res90,0,119.0,0,-res90,7.0];

Export.image.toDrive({
  image: predictors,
  description: 'Sulu_Mangrove_Driver_Predictors_90m',
  folder: 'Sulu_Mangrove_Research',
  fileNamePrefix: 'Sulu_Mangrove_Driver_Predictors_90m',
  region: exportBounds,
  crs: 'EPSG:4326',
  crsTransform: transform90,
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF',
  formatOptions: {cloudOptimized: true}
});
