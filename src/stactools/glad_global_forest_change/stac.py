import os
import re
from datetime import datetime, timezone
from typing import Any, Dict

import rasterio.transform
import semver
from pystac import (
    Asset,
    Collection,
    Extent,
    Item,
    ItemAssetDefinition,
    Link,
    MediaType,
    Provider,
    ProviderRole,
    RelType,
    SpatialExtent,
    TemporalExtent,
    get_stac_version,
)
from pystac.extensions.classification import (
    Classification,
    ItemAssetsClassificationExtension,
)
from pystac.extensions.render import Render, RenderExtension
from pystac.extensions.scientific import Publication
from shapely.geometry import box, mapping

from stactools.glad_global_forest_change.constants import (
    COLLECTION_ID,
    COLOR_HINTS,
    DATAMASK_ASSET_NAME,
    DATASET_HOMEPAGE,
    DESCRIPTION,
    EPSG,
    GAIN_ASSET_NAME,
    ITEM_ASSETS,
    ITEM_SHAPE,
    KEYWORDS,
    LANDSAT_FIRST_ASSET_NAME,
    LANDSAT_LAST_ASSET_NAME,
    LOSSYEAR_ASSET_NAME,
    PUBLICATION_CITATION,
    PUBLICATION_DOI,
    REQUIRED_ASSETS,
    TITLE,
    TREECOVER_ASSET_NAME,
    VERSION,
)


def format_multiline_string(string: str) -> str:
    """Format a multi-line string for use in metadata fields"""
    return re.sub(r" +", " ", re.sub(r"(?<!\n)\n(?!\n)", " ", string))


def parse_filename(filename: str) -> Dict[str, Any] | None:
    """Parse a Global Forest Change asset filename
    e.g. Hansen_GFC-2023-v1.11_gain_40N_080W.tif
    """
    pattern = r"Hansen_GFC-(\d+)-v([\d\.]+)_([a-z0-9_]+)_(\d+[NS])_(\d+[EW])\.tif"
    match = re.match(pattern, filename)

    if match:
        year, version, layer_type, lat_str, lon_str = match.groups()

        asset_key_mapping = {
            "treecover2000": TREECOVER_ASSET_NAME,
            "lossyear": LOSSYEAR_ASSET_NAME,
            "gain": GAIN_ASSET_NAME,
            "datamask": DATAMASK_ASSET_NAME,
            "last": LANDSAT_LAST_ASSET_NAME,
            "first": LANDSAT_FIRST_ASSET_NAME,
        }

        asset_key = asset_key_mapping.get(layer_type)
        if not asset_key:
            return None

        lat_direction = lat_str[-1]
        lat_value = float(lat_str[:-1])
        latitude = lat_value if lat_direction == "N" else -lat_value

        lon_direction = lon_str[-1]
        lon_value = float(lon_str[:-1])
        longitude = lon_value if lon_direction == "E" else -lon_value
        bbox = (longitude, latitude - 10, longitude + 10, latitude)
        return {
            "asset_key": asset_key,
            "id": f"hansen-gfc-{year}-v{version}-{lat_str}-{lon_str}",
            "datetime": datetime(year=int(year), month=12, day=31, tzinfo=timezone.utc),
            "version": version,
            "bbox": bbox,
            "geometry": mapping(box(*bbox)),
        }
    else:
        return None


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return "{:02x}{:02x}{:02x}".format(r, g, b)


def create_collection(
    cogs: bool = False,
    include_landsat_assets: bool = False,
) -> Collection:
    """Creates a STAC Collection.

    Returns:
        Collection: STAC Collection object
    """
    item_asset_keys = [
        LOSSYEAR_ASSET_NAME,
        GAIN_ASSET_NAME,
        TREECOVER_ASSET_NAME,
        DATAMASK_ASSET_NAME,
    ]

    if include_landsat_assets:
        item_asset_keys.extend([LANDSAT_FIRST_ASSET_NAME, LANDSAT_LAST_ASSET_NAME])

    extent = Extent(
        SpatialExtent([[-180.0, -90.0, 180.0, 90.0]]),
        TemporalExtent(
            [
                [
                    datetime(2000, 1, 1, tzinfo=timezone.utc),
                    datetime(2023, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
                ]
            ]
        ),
    )

    collection = Collection(
        id=COLLECTION_ID,
        title=TITLE,
        description=format_multiline_string(DESCRIPTION),
        keywords=KEYWORDS,
        extent=extent,
        license="CC-BY-4.0",
        providers=[
            Provider(
                name="Google",
                url=DATASET_HOMEPAGE,
                roles=[
                    ProviderRole.HOST,
                ],
            ),
            Provider(
                name="University of Maryland Global Land Analysis & Discovery "
                "laboratory (GLAD)",
                url="https://glad.umd.edu",
                roles=[
                    ProviderRole.LICENSOR,
                    ProviderRole.PRODUCER,
                ],
            ),
        ],
    )

    collection.item_assets = {
        asset_key: ItemAssetDefinition.create(
            media_type=MediaType.COG if cogs else MediaType.GEOTIFF,
            **ITEM_ASSETS[asset_key],
        )
        for asset_key in item_asset_keys
    }

    collection.add_link(
        Link(
            rel=RelType.LICENSE,
            target="https://creativecommons.org/licenses/by/4.0/",
            media_type=MediaType.HTML,
            title="CC-BY-4.0 license",
        ),
    )

    # classification values
    lossyear_classification = ItemAssetsClassificationExtension(
        collection.item_assets[LOSSYEAR_ASSET_NAME]
    )
    lossyear_classification.classes = [
        Classification.create(
            value=0,
            description="no loss",
            name="no-loss",
        )
    ] + [
        Classification.create(
            value=i,
            description=f"forest lost in {2000 + i}",
            name=f"forest-lost-{2000 + i}",
            color_hint=rgb_to_hex(*COLOR_HINTS[LOSSYEAR_ASSET_NAME][i]),
        )
        for i in range(1, 24)
    ]

    gain_classification = ItemAssetsClassificationExtension(
        collection.item_assets[GAIN_ASSET_NAME]
    )
    gain_classification.classes = [
        Classification.create(
            value=0,
            description="no forest gain between 2000 and 2012",
            name="no-gain",
            color_hint=rgb_to_hex(*COLOR_HINTS[GAIN_ASSET_NAME][0]),
        ),
        Classification.create(
            value=1,
            description="forest loss between 2000 and 2023",
            name="gain",
            color_hint=rgb_to_hex(*COLOR_HINTS[GAIN_ASSET_NAME][1]),
        ),
    ]

    datamask_classification = ItemAssetsClassificationExtension(
        collection.item_assets[DATAMASK_ASSET_NAME]
    )
    datamask_classification.classes = [
        Classification.create(
            value=0,
            description="no data",
            name="nodata",
            nodata=True,
        ),
        Classification.create(
            value=1,
            description="mapped land survace",
            name="maaped-land-surface",
        ),
        Classification.create(
            value=2,
            description="persistent water bodies",
            name="persistent-water-bodies",
        ),
    ]

    collection.ext.add("version")
    collection.ext.version.version = VERSION

    collection.ext.add("sci")
    collection.ext.sci.publications = [
        Publication(
            doi=PUBLICATION_DOI,
            citation=format_multiline_string(PUBLICATION_CITATION),
        )
    ]

    # if using STAC v1.0.0, add raster and item-assets extensions
    if semver.Version.parse(get_stac_version()) <= semver.Version.parse("1.0.0"):
        collection.ext.add("raster")
        collection.ext.add("item_assets")

    # add render extension
    collection.ext.add("render")
    renders = {
        asset_key: Render.create(
            assets=[asset_key],
            colormap={str(value): rgb for value, rgb in COLOR_HINTS[asset_key].items()},
        )
        for asset_key in item_asset_keys
        if COLOR_HINTS.get(asset_key)
    }

    renders[TREECOVER_ASSET_NAME] = Render.create(
        assets=[TREECOVER_ASSET_NAME],
        colormap={str(i): (0, int(255 * i / 100), 0) for i in range(0, 101)},
    )

    # TODO: add cool RGB mask + tree cover + gain + loss visualization!

    RenderExtension.ext(collection).apply(renders)

    return collection


def create_item(asset_hrefs: list[str], cogs: bool = False) -> Item:
    """Creates a STAC item from a list of asset hrefs.

    Args:
        asset_hrefs (list[str]): List of HREFs pointing to the assets
            associated with the item
        cogs (bool): Set to True if assets are COGs

    Returns:
        Item: STAC Item object
    """
    if not asset_hrefs:
        raise ValueError("No asset hrefs provided")

    # Parse all assets and group by their canonical keys
    assets_by_key = {}
    item_attributes = None

    for href in asset_hrefs:
        basename = os.path.basename(href)
        parsed = parse_filename(basename)

        if not parsed:
            raise ValueError(f"could not parse attributes from {href}")

        assets_by_key[parsed["asset_key"]] = href

        if item_attributes is None:
            item_attributes = parsed
        else:
            if parsed["id"] != item_attributes["id"]:
                raise ValueError(
                    f"the item ID from {href} does not match the first one provided:",
                    item_attributes["id"],
                )

    if not item_attributes:
        raise ValueError("could not parse these hrefs:", asset_hrefs)

    if missing_assets := [key for key in REQUIRED_ASSETS if key not in assets_by_key]:
        raise ValueError(f"Missing required assets: {', '.join(missing_assets)}")

    assets = {}
    for asset_key, asset_href in assets_by_key.items():
        assets[asset_key] = Asset(
            href=asset_href,
            media_type=MediaType.COG if cogs else MediaType.GEOTIFF,
            **ITEM_ASSETS[asset_key],
        )

    item = Item(
        id=item_attributes["id"],
        bbox=item_attributes["bbox"],
        geometry=item_attributes["geometry"],
        datetime=item_attributes["datetime"],
        assets=assets,
        properties={},
    )

    item.ext.add("proj")
    item.ext.proj.apply(
        epsg=EPSG,
        geometry=item_attributes["geometry"],
        bbox=item_attributes["bbox"],
        shape=ITEM_SHAPE,
        transform=rasterio.transform.from_bounds(*item_attributes["bbox"], *ITEM_SHAPE),
    )

    if semver.Version.parse(get_stac_version()) <= semver.Version.parse("1.0.0"):
        item.ext.add("raster")

    assert isinstance(item, Item)

    return item
