"""
Cloudflare R2 Upload Script

This script provides functionality to upload files and directories to Cloudflare R2 storage.
It can be run as a standalone script or imported as a module in other Python scripts.

Usage:
    As a script: python cloudflare_r2_upload.py <path> -b <base_path>
    As a module: from cloudflare_r2_upload import upload
"""

import os
import hashlib
import argparse
import mimetypes
from typing import Dict, Any
from botocore.exceptions import ClientError
from cloudflare_r2 import CloudflareR2


def calculate_md5(file_path: str) -> str:
    """
    Calculate the MD5 hash of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: MD5 hash of the file.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def file_exists(cloudflare_r2: CloudflareR2, key: str) -> bool:
    """
    Check if a file exists in the R2 bucket.

    Args:
        cloudflare_r2 (CloudflareR2): The CloudflareR2 instance class
        key (str): The key of the file in the bucket.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    try:
        cloudflare_r2.s3.head_object(Bucket=cloudflare_r2.bucket_name, Key=key)
        return True
    except ClientError:
        return False


def upload_file(cloudflare_r2: CloudflareR2, file_path: str, relative_path: str) -> None:
    """
    Upload a single file to the R2 bucket.

    Args:
        cloudflare_r2 (CloudflareR2): The CloudflareR2 instance class
        file_path (str): Path to the local file.
        relative_path (str): Relative path to use as the key in the bucket.
    """
    try:
        if ".DS_Store" in file_path:
            print(f"Ignoring {file_path}")
            return

        key: str = relative_path.replace("\\", "/")
        local_md5: str = calculate_md5(file_path)

        if file_exists(cloudflare_r2, key):
            remote_obj: Dict[str, Any] = cloudflare_r2.s3.head_object(Bucket=cloudflare_r2.bucket_name, Key=key)
            remote_md5: str = remote_obj['ETag'].strip('"')

            if local_md5 == remote_md5:
                print(f"File {key} already exists and is up to date. Skipping.")
                return

            print(f"File {key} exists but has changed. Updating...")
        else:
            print(f"Uploading new file {key}...")

        mime = mimetypes.guess_type(file_path)[0]
        with open(file_path, 'rb') as file:
            cloudflare_r2.s3.put_object(Bucket=cloudflare_r2.bucket_name, Key=key, Body=file, ContentType=mime)
        print(f"Successfully uploaded {key} with ContentType {mime}")
    except ClientError as e:
        print(f"Error uploading {key}: {str(e)}")


def upload(cloudflare_r2: CloudflareR2, path: str, base_path: str) -> None:
    """
    Upload a file or directory to the R2 bucket.

    Args:
        cloudflare_r2 (CloudflareR2): The CloudflareR2 instance class
        path (str): Path to the file or directory to upload.
        base_path (str): Base path to use as the root in R2.
    """
    if os.path.isfile(path):
        relative_path: str = os.path.relpath(path, start=os.path.dirname(base_path))
        upload_file(cloudflare_r2, path, relative_path)
        return

    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_path: str = os.path.join(root, file)
                relative_path: str = os.path.relpath(file_path, start=os.path.dirname(base_path))
                upload_file(cloudflare_r2, file_path, relative_path)
        return

    print(f"Invalid path: {path}")


def main() -> None:
    """
    Main function to handle command-line arguments and initiate the upload process.
    """
    parser = argparse.ArgumentParser(
        description="Upload file or directory to Cloudflare R2")
    parser.add_argument("path", help="Path to file or directory to upload")
    parser.add_argument("-b", "--base_path", required=True,
                        help="""Base path to use as the root in R2.
                        The local directory structure will be mirrored in R2 from here down.""")
    args = parser.parse_args()

    try:
        cloudflare_r2 = CloudflareR2()
        upload(cloudflare_r2, args.path, args.base_path)
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please ensure all required environment variables are set.")


if __name__ == "__main__":
    main()
