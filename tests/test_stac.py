import pytest
from pystac import MediaType

from stactools.glad_global_forest_change import stac
from stactools.glad_global_forest_change.constants import (
    COLLECTION_ID,
    LOSSYEAR_ASSET_NAME,
    REQUIRED_ASSETS,
)

URL_FORMAT = "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_{asset}_{loc}.tif"


def test_create_collection() -> None:
    # This function should be updated to exercise the attributes of interest on
    # the collection

    collection = stac.create_collection()
    collection.set_self_href(None)  # required for validation to pass
    assert collection.id == COLLECTION_ID
    assert collection.item_assets[LOSSYEAR_ASSET_NAME].media_type == MediaType.GEOTIFF
    collection.validate()


def test_create_item() -> None:
    item = stac.create_item(
        [URL_FORMAT.format(asset=asset, loc="20N_000E") for asset in REQUIRED_ASSETS]
    )
    assert item.id == "hansen-gfc-2023-v1.11-20N-000E"
    item.validate()

    # make sure we get an error if mismatched hrefs are provided
    with pytest.raises(ValueError):
        stac.create_item(
            [
                URL_FORMAT.format(asset=asset, loc="20N_000E")
                for asset in REQUIRED_ASSETS[:3]
            ]
            + [URL_FORMAT.format(asset=REQUIRED_ASSETS[3], loc="20N_010E")]
        )

    # make sure we get an error if an href refers to a non-existent asset
    with pytest.raises(ValueError):
        stac.create_item(
            [
                URL_FORMAT.format(asset=asset, loc="20N_000E")
                for asset in REQUIRED_ASSETS[:3]
            ]
            + [URL_FORMAT.format(asset="nope", loc="20N_000E")]
        )

    # make sure we get an error if not all required assets are provided
    with pytest.raises(ValueError):
        stac.create_item(
            [
                URL_FORMAT.format(asset=asset, loc="20N_000E")
                for asset in REQUIRED_ASSETS[:3]
            ]
        )
