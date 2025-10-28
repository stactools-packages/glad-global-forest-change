import stactools.core
from stactools.cli.registry import Registry

from stactools.glad_global_forest_change.stac import create_collection, create_item

__all__ = ["create_collection", "create_item"]

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    from stactools.glad_global_forest_change import commands

    registry.register_subcommand(commands.create_gladglobalforestchange_command)
