import logging

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
    def create_collection_command(destination: str) -> None:
        """Creates a STAC Collection

        Args:
            destination: An HREF for the Collection JSON
        """
        collection = stac.create_collection()
        collection.set_self_href(destination)
        collection.save_object()

    @gladglobalforestchange.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(source: str, destination: str) -> None:
        """Creates a STAC Item

        Args:
            source: HREF of the Asset associated with the Item
            destination: An HREF for the STAC Item
        """
        item = stac.create_item(source)
        item.save_object(dest_href=destination)

    return gladglobalforestchange
