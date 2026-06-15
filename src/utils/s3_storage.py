import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


load_dotenv()


def use_s3_storage() -> bool:
    return os.getenv("USE_S3_STORAGE", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_bucket() -> str:
    bucket = os.getenv("S3_BUCKET", "").strip()

    if not bucket:
        raise ValueError("S3_BUCKET is required when USE_S3_STORAGE=true.")

    return bucket


def get_prefix() -> str:
    return os.getenv("S3_PREFIX", "").strip("/")


def build_s3_key(*parts: str) -> str:
    key_parts = []
    prefix = get_prefix()

    if prefix:
        key_parts.append(prefix)

    key_parts.extend(
        str(part).strip("/")
        for part in parts
        if str(part).strip("/")
    )

    return "/".join(key_parts)


def get_s3_client():
    region = os.getenv("AWS_REGION", "").strip()

    if region:
        return boto3.client("s3", region_name=region)

    return boto3.client("s3")


def download_file(
    s3_key: str,
    local_path: Path,
    required: bool = True,
) -> Path:
    local_path = Path(local_path)

    if not use_s3_storage():
        return local_path

    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        get_s3_client().download_file(
            get_bucket(),
            s3_key,
            str(local_path),
        )
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code", "")

        if not required and error_code in {"404", "NoSuchKey"}:
            return local_path

        raise

    return local_path


def upload_file(
    local_path: Path,
    s3_key: str,
) -> str:
    local_path = Path(local_path)

    if not use_s3_storage():
        return s3_key

    get_s3_client().upload_file(
        str(local_path),
        get_bucket(),
        s3_key,
    )

    return s3_key


def download_prefix(
    s3_prefix: str,
    local_dir: Path,
    suffix: str | None = None,
) -> list[Path]:
    local_dir = Path(local_dir)

    if not use_s3_storage():
        return list(local_dir.glob(f"*{suffix or ''}"))

    local_dir.mkdir(parents=True, exist_ok=True)
    downloaded_files = []
    paginator = get_s3_client().get_paginator("list_objects_v2")

    for page in paginator.paginate(
        Bucket=get_bucket(),
        Prefix=s3_prefix,
    ):
        for item in page.get("Contents", []):
            key = item["Key"]

            if key.endswith("/"):
                continue

            if suffix and not key.endswith(suffix):
                continue

            relative_key = key[len(s3_prefix):].lstrip("/")
            local_path = local_dir / relative_key
            local_path.parent.mkdir(parents=True, exist_ok=True)

            get_s3_client().download_file(
                get_bucket(),
                key,
                str(local_path),
            )

            downloaded_files.append(local_path)

    return downloaded_files
