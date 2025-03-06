"""Constants for stactools.global_forest_change"""

from typing import Any, Dict

VERSION = "1.11"
COLLECTION_ID = f"glad-global-forest-change-{VERSION}"
TITLE = f"GLAD: Global Forest Change 2000-2023 v{VERSION}"
KEYWORDS = ["forest", "change", "deforestation"]

DATASET_HOMEPAGE = "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/download.html"

PUBLICATION_DOI = "10.1126/science.1244693"

PUBLICATION_CITATION = """Hansen, M. C., P. V. Potapov, R. Moore, M. Hancher, S. A. 
Turubanova, A. Tyukavina, D. Thau, S. V. Stehman, S. J. Goetz, T. R. Loveland, 
A. Kommareddy, A. Egorov, L. Chini, C. O. Justice, and J. R. G. Townshend. 2013. 
High-Resolution Global Maps of 21st-Century Forest Cover Change. Science 342 
(15 November): 850-53. Data available on-line from: 
https://glad.earthengine.app/view/global-forest-change."""

DESCRIPTION = """Results from time-series analysis of Landsat images in characterizing
global forest extent and change from 2000 through 2023. For additional information 
about these results, please see the associated journal article (Hansen et al., Science 
2013).

Web-based visualizations of these results are also available at our main site:

> https://glad.earthengine.app/view/global-forest-change

Please use that URL when linking to this dataset.

We anticipate releasing updated versions of this dataset. To keep up to date with the 
latest updates, and to help us better understand how these data are used, please 
[register as a user](https://docs.google.com/a/google.com/forms/d/1AkAUb4kfF7pUTOADPGEW7Do2oRhdDUPYb2mzIr8OIx4/viewform)
. Thanks!
"""


TREECOVER_ASSET_NAME = "treecover2000"
GAIN_ASSET_NAME = "gain"
LOSSYEAR_ASSET_NAME = "lossyear"
DATAMASK_ASSET_NAME = "datamask"
LANDSAT_FIRST_ASSET_NAME = "first"
LANDSAT_LAST_ASSET_NAME = "last"

REQUIRED_ASSETS = [
    TREECOVER_ASSET_NAME,
    LOSSYEAR_ASSET_NAME,
    GAIN_ASSET_NAME,
    DATAMASK_ASSET_NAME,
]

ASSETS = [
    GAIN_ASSET_NAME,
    LANDSAT_FIRST_ASSET_NAME,
    LANDSAT_LAST_ASSET_NAME,
    LOSSYEAR_ASSET_NAME,
    DATAMASK_ASSET_NAME,
    TREECOVER_ASSET_NAME,
]

EPSG = 4326
ITEM_SHAPE = [40000, 40000]
DATA_TYPE = "uint8"
RASTER_BANDS_METADATA = [
    {
        "data_type": DATA_TYPE,
        "scale": 1.0,
        "offset": 0.0,
        "sampling": "area",
    }
]

ITEM_ASSETS: Dict[str, Dict[str, Any]] = {
    TREECOVER_ASSET_NAME: {
        "title": "Tree canopy cover for year 2000",
        "description": "Tree cover in the year 2000, defined as canopy closure for all "
        "vegetation taller than 5m in height. Encoded as a percentage per output grid "
        "cell, in the range 0-100.",
        "roles": ["data"],
        "extra_fields": {
            "raster:bands": RASTER_BANDS_METADATA,
        },
    },
    GAIN_ASSET_NAME: {
        "title": "Global forest cover gain 2000-2012",
        "description": "Forest gain during the period 2000-2012, defined as the "
        "inverse of loss, or a non-forest to forest change entirely within the study "
        "period. Encoded as either 1 (gain) or 0 (no gain).",
        "roles": ["data"],
        "extra_fields": {
            "raster:bands": RASTER_BANDS_METADATA,
        },
    },
    LOSSYEAR_ASSET_NAME: {
        "title": "Year of gross forest cover loss event",
        "description": "Forest loss during the period 2000-2023, defined as a "
        "stand-replacement disturbance, or a change from a forest to non-forest state. "
        "Encoded as either 0 (no loss) or else a value in the range 1-20, representing "
        "loss detected primarily in the year 2001-2023, respectively.",
        "roles": ["data"],
        "extra_fields": {"raster:bands": RASTER_BANDS_METADATA},
    },
    DATAMASK_ASSET_NAME: {
        "title": "Data mask",
        "description": "Three values representing areas of no data (0), mapped land "
        "surface (1), and persistent water bodies (2) based on 2000-2012.",
        "roles": ["data"],
        "extra_fields": {"raster:bands": RASTER_BANDS_METADATA},
    },
    LANDSAT_FIRST_ASSET_NAME: {
        "title": "Circa year 2000 Landsat 7 cloud-free image composite",
        "description": "Reference multispectral imagery from the first available year, "
        "typically 2000. If no cloud-free observations were available for year 2000, "
        "imagery was taken from the closest year with cloud-free data, within the "
        "range 1999-2012.",
        "roles": ["data"],
    },
    LANDSAT_LAST_ASSET_NAME: {
        "title": "Circa year 2023 Landsat cloud-free image composite",
        "description": "Reference multispectral imagery from the last available year, "
        "typically 2023. If no cloud-free observations were available for year 2023, "
        "imagery was taken from the closest year with cloud-free data.",
        "roles": ["data"],
    },
}

# RGB values approximated from the legend in the GEE app
COLOR_HINTS = {
    LOSSYEAR_ASSET_NAME: {
        0: (0, 0, 0),
        1: (255, 255, 0),
        2: (255, 243, 0),
        3: (255, 230, 0),
        4: (255, 217, 0),
        5: (255, 204, 0),
        6: (255, 192, 0),
        7: (255, 179, 0),
        8: (255, 166, 0),
        9: (255, 153, 0),
        10: (255, 140, 0),
        11: (255, 128, 0),
        12: (255, 116, 0),
        13: (255, 105, 0),
        14: (255, 93, 0),
        15: (255, 81, 0),
        16: (255, 70, 0),
        17: (255, 58, 0),
        18: (255, 46, 0),
        19: (255, 35, 0),
        20: (255, 23, 0),
        21: (255, 12, 0),
        22: (255, 0, 0),
        23: (0, 255, 255),
    },
    GAIN_ASSET_NAME: {
        0: (0, 0, 0),
        1: (0, 0, 255),
    },
}
