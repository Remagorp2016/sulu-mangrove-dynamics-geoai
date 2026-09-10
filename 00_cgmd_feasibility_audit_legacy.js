// ================================================================
// SULU MANGROVE DYNAMICS RESEARCH
// Stage 03: Independent Feasibility + Uncertainty Audit using CGMD
// Dataset: Continuous Global Mangrove Dynamics (CGMD-Extent30)
// Period used here: 1995-2023
// Study area: Sulu Province, Philippines
// Prepared for Google Earth Engine Code Editor
// ================================================================

// ---------- 1. STUDY-AREA BOUNDARIES ----------
var gaul1 = ee.FeatureCollection('FAO/GAUL/2015/level1');
var gaul2 = ee.FeatureCollection('FAO/GAUL/2015/level2');

var sulu = gaul1
  .filter(ee.Filter.eq('ADM0_NAME', 'Philippines'))
  .filter(ee.Filter.eq('ADM1_NAME', 'Sulu'));

var suluMunicipalities = gaul2
  .filter(ee.Filter.eq('ADM0_NAME', 'Philippines'))
  .filter(ee.Filter.eq('ADM1_NAME', 'Sulu'));

print('Sulu province boundary feature count (should be 1):', sulu.size());
print('Sulu province boundary:', sulu);
print('Sulu municipality features:', suluMunicipalities.size());
print('Municipality names:', suluMunicipalities.aggregate_array('ADM2_NAME').sort());

var suluGeom = sulu.geometry();
Map.centerObject(sulu, 8);
Map.addLayer(
  sulu.style({color: '000000', fillColor: '00000000', width: 2}),
  {},
  'Sulu Province boundary',
  true
);

// ---------- 2. CGMD ANNUAL MANGROVE EXTENT ----------
// Earth Engine publisher dataset: annual mangrove extent, 1984-2023, 30 m.
// gridcode = 1: based on valid Landsat observations
// gridcode = 2: gap-filled from closest/latest valid observation
var cgmd = ee.FeatureCollection(
  'projects/mangrovedatahub2/assets/CGMD-Extent30'
);

var startYear = 1995;
var endYear = 2023;
var years = ee.List.sequence(startYear, endYear);

// Calculate area of a feature collection *inside Sulu*, in km2.
function clippedAreaKm2(fc) {
  var withArea = fc.map(function (f) {
    var clipped = f.geometry().intersection(suluGeom, ee.ErrorMargin(30));
    var km2 = clipped.area(30).divide(1e6);
    return f.set('_sulu_km2', km2);
  });
  return ee.Number(withArea.aggregate_sum('_sulu_km2'));
}

// ---------- 3. ANNUAL AREA + GAP-FILL QA TABLE ----------
var annualStats = ee.FeatureCollection(
  years.map(function (y) {
    y = ee.Number(y);

    var annual = cgmd
      .filter(ee.Filter.eq('year', y))
      .filterBounds(suluGeom);

    var observed = annual.filter(ee.Filter.eq('gridcode', 1));
    var gapfilled = annual.filter(ee.Filter.eq('gridcode', 2));

    var observedKm2 = clippedAreaKm2(observed);
    var gapfilledKm2 = clippedAreaKm2(gapfilled);
    var totalKm2 = observedKm2.add(gapfilledKm2);

    var gapfilledPct = ee.Number(
      ee.Algorithms.If(
        totalKm2.gt(0),
        gapfilledKm2.divide(totalKm2).multiply(100),
        0
      )
    );

    return ee.Feature(null, {
      year: y,
      mangrove_km2: totalKm2,
      mangrove_ha: totalKm2.multiply(100),
      observed_km2: observedKm2,
      observed_ha: observedKm2.multiply(100),
      gapfilled_km2: gapfilledKm2,
      gapfilled_ha: gapfilledKm2.multiply(100),
      gapfilled_pct: gapfilledPct,
      intersecting_features: annual.size()
    });
  })
).sort('year');

print('Annual Sulu mangrove area and gap-fill QA, 1995-2023:', annualStats);

// ---------- 4. QUICK TIME-SERIES CHARTS ----------
var areaChart = ui.Chart.feature.byFeature(
  annualStats,
  'year',
  ['mangrove_ha']
)
.setChartType('LineChart')
.setOptions({
  title: 'Sulu Mangrove Extent (CGMD), 1995-2023',
  hAxis: {title: 'Year'},
  vAxis: {title: 'Mangrove area (ha)'},
  lineWidth: 2,
  pointSize: 3,
  legend: {position: 'none'}
});
print(areaChart);

var gapChart = ui.Chart.feature.byFeature(
  annualStats,
  'year',
  ['gapfilled_pct']
)
.setChartType('ColumnChart')
.setOptions({
  title: 'CGMD Gap-filled Share within Sulu, 1995-2023',
  hAxis: {title: 'Year'},
  vAxis: {title: 'Gap-filled mangrove area (%)'},
  legend: {position: 'none'}
});
print(gapChart);

// ---------- 5. SNAPSHOT MAPS ----------
function addExtentLayer(year, shown) {
  var fc = cgmd
    .filter(ee.Filter.eq('year', year))
    .filterBounds(suluGeom)
    .map(function (f) {
      return f.intersection(suluGeom, ee.ErrorMargin(30));
    });

  Map.addLayer(
    fc.style({color: '006400', fillColor: '00640088', width: 1}),
    {},
    'CGMD mangrove extent ' + year,
    shown
  );
}

addExtentLayer(1995, false);
addExtentLayer(2000, false);
addExtentLayer(2010, false);
addExtentLayer(2020, false);
addExtentLayer(2023, true);

// ---------- 6. EXPORTS ----------
// Run these from the Tasks tab after the script finishes.
Export.table.toDrive({
  collection: annualStats,
  description: 'Sulu_CGMD_1995_2023_Area_GapFill_Audit',
  folder: 'Sulu_Mangrove_Research',
  fileNamePrefix: 'Sulu_CGMD_1995_2023_Area_GapFill_Audit',
  fileFormat: 'CSV'
});

Export.table.toDrive({
  collection: sulu,
  description: 'Sulu_GAUL2015_Province_Boundary',
  folder: 'Sulu_Mangrove_Research',
  fileNamePrefix: 'Sulu_GAUL2015_Province_Boundary',
  fileFormat: 'GeoJSON'
});

Export.table.toDrive({
  collection: suluMunicipalities,
  description: 'Sulu_GAUL2015_Municipal_Boundaries',
  folder: 'Sulu_Mangrove_Research',
  fileNamePrefix: 'Sulu_GAUL2015_Municipal_Boundaries',
  fileFormat: 'GeoJSON'
});

// ---------- 7. INTERPRETATION RULES FOR OUR STUDY ----------
// Main GMW study: 1995-2025 (30-year interval; 31 annual epochs).
// Main driver modelling: 2000-2025, because GMW warns of reduced
// satellite availability in parts of the 1980s/1990s.
// CGMD is an independent validation series through 2023.
// A sustained-change filter (>= 3 years) will be used later to reduce
// sensitivity to one-year classification noise/transient disturbance.
// ================================================================
