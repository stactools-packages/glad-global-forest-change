# stactools-glad-global-forest-change

[![PyPI](https://img.shields.io/pypi/v/stactools-glad-global-forest-change?style=for-the-badge)](https://pypi.org/project/stactools-glad-global-forest-change/)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/stactools-packages/glad-global-forest-change/continuous-integration.yml?style=for-the-badge)

- Name: glad-global-forest-change
- Package: `stactools.glad_global_forest_change`
- [stactools-glad-global-forest-change on PyPI](https://pypi.org/project/stactools-glad-global-forest-change/)
- Owner: @hrodmn
- [Dataset homepage](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/download.html)
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
  - [raster](https://github.com/stac-extensions/raster/)
  - [render](https://github.com/stac-extensions/render/)
  - [version](https://github.com/stac-extensions/version/)
  - [scientific](https://github.com/stac-extensions/scientific/)
  - [item-assets](https://github.com/stac-extensions/item-assets/)
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/glad-global-forest-change/main/examples/collection.json)
- [Browse a notebook demonstrating the example item and collection](https://github.com/stactools-packages/glad-global-forest-change/tree/main/docs/example.ipynb)

## STAC examples

- [Collection](examples/collection.json)
- [Item](examples/item/item.json)

## Installation

```shell
pip install stactools-glad-global-forest-change
```

## Command-line usage

By default, `stactools-glad-global-forest-change` will assume that you are generating STAC metadata for the original files which are stored in a Google storage container and publicly available over HTTP.

```bash
stac gladglobalforestchange create-collection {destination}

stac gladglobalforestchange create-item \
  https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_gain_40N_080W.tif \
  https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_treecover2000_40N_080W.tif \
  https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_lossyear_40N_080W.tif \
  https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_datamask_40N_080W.tif \
  /tmp/item.json    
```

> [!WARNING]  
> These files are not cloud-optimized geotiffs (COGs)!
> Be aware that this has major performance implications for applications that consume the data from these assets.
> Consider creating a copy of the files in the COG format and providing the `--cogs` flag to indicate that the
assets are COGs.

Use `stac gladglobalforestchange --help` to see all subcommands and options.

## Create COGs

The original files hosted on the Google Earth Engine are not cloud-optimized geotiffs (COGs).
This is a problem for many applications so we added the `create-cogs` function to convert the underlying
assets to COGs and copy them to a new storage location (either a local directory or an S3 bucket).

```bash
stac gladglobalforestchange create-cogs {assets} {destination} --region={region}
```

> [!NOTE]
> The `create-cogs` function uses [`coiled`](https://www.coiled.io/) to run the translate-and-upload
> operations for thousands of files. If you run it in AWS you can expect the total cost to be
> less than $2 for compute which is well within the free-tier for `coiled`.

## Contributing

We use [pre-commit](https://pre-commit.com/) to check any changes.
To set up your development environment:

```shell
uv sync
uv run pre-commit install
```

To check all files:

```shell
uv run pre-commit run --all-files
```

To run the tests:

```shell
uv run pytest -vv
```

If you've updated the STAC metadata output, update the examples:

```shell
uv run scripts/update-examples
```
