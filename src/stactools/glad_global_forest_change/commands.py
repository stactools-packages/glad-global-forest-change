import logging
from typing import Tuple

import click
from click import Command, Group

from stactools.glad_global_forest_change import stac

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

    return gladglobalforestchange
