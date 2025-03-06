from pathlib import Path

from rio_cogeo.cogeo import cog_validate

from stactools.glad_global_forest_change.cogs import create_cogs
from stactools.glad_global_forest_change.constants import REQUIRED_ASSETS

from . import test_data


def test_create_cogs(tmp_path: Path) -> None:
    cogs = create_cogs(
        file_list=[
            f"Hansen_GFC-2023-v1.11_{asset}_40N_080W.tif" for asset in REQUIRED_ASSETS
        ],
        destination=str(tmp_path),
        base_url="file://" + test_data.get_path("data"),
    )

    assert len(cogs) == len(REQUIRED_ASSETS)

    for cog in cogs:
        valid, _, _ = cog_validate(tmp_path / cog)
        assert valid
