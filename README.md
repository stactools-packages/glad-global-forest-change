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
stac gladglobalforestchange create-collection \
  --sample-asset-href https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_gain_40N_080W.tif \
  {destination}

stac gladglobalforestchange create-item \
  https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_gain_40N_080W.tif \
  {destination}
```

> [!WARNING]  
> These files are not cloud-optimized geotiffs (COGs)!
> Be aware that this has major performance implications for applications that consume the data from these assets.

If you have created your own copy of the data in a different storage container, you can provide a custom URL format for the assets with the `--href-format` parameter in the `create-item` command:

```bash

stac gladglobalforestchange create-collection \
  --sample-asset-href {sample_tif_url} \
  {destination}

stac gladglobalforestchange create-item \
  --href-format s3://bucket/glad/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_{asset}_{loc}.tif \
  {cog_href} \
  {destination}
```

Use `stac gladglobalforestchange --help` to see all subcommands and options.

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
