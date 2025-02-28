"""Create COGs from the original files and upload them to S3

Since we are using obstore we could update the script to work in other
cloud environments in theory.
"""

import io
import urllib.parse
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

import httpx
import rasterio
from rasterio.io import MemoryFile

from stactools.glad_global_forest_change.constants import ASSETS

BASE_URL = "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11"


def to_url(s: str) -> str:
    """Make sure a string is a URL"""
    if urllib.parse.urlparse(s).scheme:
        return s
    else:
        return "file://" + str(Path(s).absolute())


def get_file_list(assets: Tuple[str, ...]) -> List[str]:
    """Get the list of raw files for a set of assets"""
    file_list: List[str] = []
    for asset in assets:
        if asset not in ASSETS:
            raise ValueError(f"{asset} is not a valid layer. must be one of {ASSETS}")

        file_list_url = BASE_URL + f"/{asset}.txt"
        request = httpx.get(file_list_url)
        file_list.extend(
            file.replace(BASE_URL + "/", "") for file in request.iter_lines()
        )

    return file_list


def cogify(
    source_file: str,
    destination: str,
    config: Dict[str, Any],
    base_url: str = BASE_URL,
) -> str:
    import obstore.store
    from rio_cogeo.cogeo import cog_translate
    from rio_cogeo.profiles import cog_profiles

    dst_profile = cog_profiles.get("deflate")
    config = dict(
        GDAL_TIFF_INTERNAL_MASK=True,
        GDAL_TIFF_OVR_BLOCKSIZE="128",
    )

    source_store = obstore.store.from_url(
        url=base_url,
        client_options={"timeout": timedelta(minutes=5)},
    )

    destination_store = obstore.store.from_url(
        destination,
        **config,
    )

    response = obstore.get(source_store, source_file)
    data = bytes(response.bytes())

    with (
        rasterio.open(io.BytesIO(data)) as src,
        MemoryFile() as dst_memfile,
    ):
        cog_translate(
            src,
            dst_memfile.name,
            dst_profile,
            in_memory=True,
            quiet=True,
            config=config,
        )

        obstore.put(destination_store, source_file, dst_memfile)

    return source_file


def create_cogs(
    file_list: List[str],
    destination: str,
    region: str,
    base_url: str = BASE_URL,
    use_coiled: bool = False,
) -> List[str]:
    """Convert a list of raw files into COGs and upload to storage

    This function uses coiled to parallelize this resource-intensive transfer
    operation. For more information on how to get started check out the coiled
    docs: https://docs.coiled.io/user_guide/index.html#
    """
    import boto3
    from tqdm import tqdm

    destination = to_url(destination)

    protocol = urllib.parse.urlparse(destination).scheme
    local = destination.startswith("file://")

    if protocol == "s3":
        session = boto3.Session()
        credentials = session.get_credentials()
        frozen_credentials = credentials.get_frozen_credentials()

        config = {
            "aws_access_key_id": frozen_credentials.access_key,
            "aws_secret_access_key": frozen_credentials.secret_key,
            "aws_session_token": frozen_credentials.token,
            "region": session.region_name,
        }
    elif protocol == "file":
        config = {}
    else:
        raise ValueError(
            f"{protocol} is not supported. please use either file:// or s3://"
        )

    if use_coiled:
        import coiled

        _cogify = coiled.function(
            region=region,
            threads_per_worker=-1,
            n_workers=[0, 100],
            local=local,
        )(cogify)

        _cogs = _cogify.map(
            file_list, destination=destination, config=config, base_url=base_url
        )

        cogs = []
        for _cog in tqdm(_cogs, total=len(file_list)):
            cogs.append(_cog)
    else:
        cogs = [
            cogify(
                source_file, destination=destination, config=config, base_url=base_url
            )
            for source_file in tqdm(file_list)
        ]

    print(f"transferred {len(cogs)} COGs to {destination}")

    return cogs
