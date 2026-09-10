from pathlib import Path
import yaml
import numpy as np
import rasterio
from pyproj import Geod


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)


def require_files(paths):
    missing = [str(p) for p in paths if not Path(p).exists()]
    if missing:
        raise FileNotFoundError('Missing required input files:\n  ' + '\n  '.join(missing))


def geodesic_pixel_area_grid(transform, height, width):
    """Approximate geodesic pixel area (ha), constant across columns within a row."""
    geod = Geod(ellps='WGS84')
    rows = np.empty(height, dtype='float64')
    for r in range(height):
        x0, y0 = rasterio.transform.xy(transform, r, 0, offset='ul')
        x1, y1 = rasterio.transform.xy(transform, r, 0, offset='lr')
        area, _ = geod.polygon_area_perimeter([x0,x1,x1,x0],[y0,y0,y1,y1])
        rows[r] = abs(area) / 10000.0
    return np.broadcast_to(rows[:, None], (height, width))
