from pathlib import Path

from click import Group
from click.testing import CliRunner
from pystac import Collection, Item

from stactools.glad_global_forest_change.commands import (
    create_gladglobalforestchange_command,
)

command = create_gladglobalforestchange_command(Group())


def test_create_collection(tmp_path: Path) -> None:
    # Smoke test for the command line create-collection command
    #
    # Most checks should be done in test_stac.py::test_create_collection

    path = str(tmp_path / "collection.json")
    runner = CliRunner()
    result = runner.invoke(command, ["create-collection", path])
    assert result.exit_code == 0, "\n{}".format(result.output)
    collection = Collection.from_file(path)
    collection.validate()


def test_create_item(tmp_path: Path) -> None:
    # Smoke test for the command line create-item command
    #
    # Most checks should be done in test_stac.py::test_create_item
    path = str(tmp_path / "item.json")
    asset_hrefs = (
        "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_gain_20N_000E.tif",
        "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_treecover2000_20N_000E.tif",
        "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_lossyear_20N_000E.tif",
        "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_datamask_20N_000E.tif",
    )
    runner = CliRunner()
    result = runner.invoke(command, ["create-item", *asset_hrefs, path])
    assert result.exit_code == 0, "\n{}".format(result.output)
    item = Item.from_file(path)
    item.validate()
