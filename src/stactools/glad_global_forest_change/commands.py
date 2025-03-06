import logging
from typing import Tuple

import click
from click import Command, Group

from stactools.glad_global_forest_change import stac
from stactools.glad_global_forest_change.cogs import create_cogs, get_file_list
from stactools.glad_global_forest_change.constants import ASSETS

logger = logging.getLogger(__name__)


def create_gladglobalforestchange_command(cli: Group) -> Command:
    """Creates the stactools-glad-global-forest-change command line utility."""

    @cli.group(
        "gladglobalforestchange",
        short_help=("Commands for working with stactools-glad-global-forest-change"),
    )
    def gladglobalforestchange() -> None:
        pass

    @gladglobalforestchange.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    @click.option(
        "--cogs",
        is_flag=True,
        help="Indicate that assets are stored as COGs",
        default=False,
    )
    def create_collection_command(
        destination: str,
        cogs: bool = False,
    ) -> None:
        """Creates a STAC Collection

        Args:
            destination: An HREF for the Collection JSON
        """
        collection = stac.create_collection(cogs=cogs)
        collection.set_self_href(destination)
        collection.save_object()

    @gladglobalforestchange.command(
        "create-item",
        short_help="Creates a STAC item",
    )
    @click.argument("asset_hrefs", nargs=-1, required=True)
    @click.argument("destination")
    @click.option(
        "--cogs",
        is_flag=True,
        help="Indicate that assets are stored as COGs",
        default=False,
    )
    def create_item_command(
        asset_hrefs: Tuple[str, ...],
        destination: str,
        cogs: bool = False,
    ) -> None:
        """Creates a STAC Item

        Args:
            asset_hrefs: One or more HREFs of the assets to include in the item
            destination: An HREF for the STAC Item JSON output
        """
        if len(asset_hrefs) < 1:
            raise click.UsageError("At least one asset HREF is required")

        logger.info(f"Creating item from {len(asset_hrefs)} assets")
        logger.info(f"Saving item to {destination}")

        item = stac.create_item(
            asset_hrefs=list(asset_hrefs),
            cogs=cogs,
        )
        item.save_object(dest_href=destination)

    @gladglobalforestchange.command(
        "create-cogs",
        short_help="Convert original files to COGs and upload to cloud storage",
    )
    @click.argument(
        "assets",
        nargs=-1,
        required=True,
        type=click.Choice(ASSETS, case_sensitive=False),
    )
    @click.argument(
        "destination",
        required=True,
    )
    def create_cogs_command(
        assets: Tuple[str, ...],
        destination: str,
    ) -> None:
        f"""Create COG copies of ASSETS at DESTINATION in the REGION region in AWS

        ASSETS are the names of the assets that you want to copy ({", ".join(ASSETS)})

        DESTINATION is the destination location in S3, e.g. s3://bucket/prefix or a 
        local directory
        """
        file_list = get_file_list(assets)
        create_cogs(
            file_list=file_list,
            destination=destination,
        )

    return gladglobalforestchange
