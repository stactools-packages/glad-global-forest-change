"""Create COGs from the original files and upload them to S3

Since we are using obstore we could update the script to work in other
cloud environments in theory.
"""

import io
import urllib.parse
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

import rasterio
from rasterio.io import MemoryFile

from stactools.glad_global_forest_change.constants import ASSETS

BASE_URL = "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11"


def to_url(s: str) -> str:
    """Make sure a string is a URL"""
    if urllib.parse.urlparse(s).scheme:
        return s
    else:
        return f"file://{str(Path(s).absolute())}"


def get_file_list(assets: Tuple[str, ...]) -> List[str]:
    """Get the list of raw files for a set of assets"""
    import httpx

    file_list: List[str] = []
    for asset in assets:
        if asset not in ASSETS:
            raise ValueError(f"{asset} is not a valid layer. must be one of {ASSETS}")

        file_list_url = f"{BASE_URL}/{asset}.txt"
        request = httpx.get(file_list_url)
        file_list.extend(
            file.replace(f"{BASE_URL}/", "") for file in request.iter_lines()
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
    base_url: str = BASE_URL,
) -> List[str]:
    """Convert a list of raw files into COGs and upload to storage"""
    import boto3
    from tqdm import tqdm

    destination = to_url(destination)

    protocol = urllib.parse.urlparse(destination).scheme

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

    cogs = [
        cogify(source_file, destination=destination, config=config, base_url=base_url)
        for source_file in tqdm(file_list)
    ]

    print(f"transferred {len(cogs)} COGs to {destination}")

    return cogs
