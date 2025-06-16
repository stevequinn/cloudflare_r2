"""
Cloudflare R2 Delete Script

This script provides functionality to delete files and directories from Cloudflare R2 storage.
It can be run as a standalone script or imported as a module in other Python scripts.

Usage:
    As a script: python cloudflare_r2_delete.py <path>
                python cloudflare_r2_delete.py <path> --bucket <bucket_name>
    As a module: from cloudflare_r2_delete import delete
"""
import argparse
from typing import List
from cloudflare_r2 import CloudflareR2


def delete(cloudflare_r2: CloudflareR2, path: str) -> None:
    """
    Delete a file or folder within a Cloudflare R2 bucket.

    Args:
        cloudflare_r2 (CloudflareR2): The CloudflareR2 instance class
        path (str): The path of the file or folder to delete (e.g. "path/to/file" or "path/to/folder")
    """
    path_components: List[str] = path.split('/')

    if path_components[-1] == '':
        path_components.pop()
        folder_path: str = '/'.join(path_components)
        objects = cloudflare_r2.s3.list_objects(Bucket=cloudflare_r2.bucket_name, Prefix=folder_path)

        for obj in objects.get('Contents', []):
            print(f'Deleting {obj["Key"]}')
            cloudflare_r2.s3.delete_object(Bucket=cloudflare_r2.bucket_name, Key=obj['Key'])

        print(f'Deleting folder {folder_path}/')
        cloudflare_r2.s3.delete_object(Bucket=cloudflare_r2.bucket_name, Key=folder_path + '/')
    else:
        print(f'Deleting file {path}')
        cloudflare_r2.s3.delete_object(Bucket=cloudflare_r2.bucket_name, Key=path)


def main() -> None:
    """
    Main function to handle command-line arguments and initiate the delete process.
    """
    parser = argparse.ArgumentParser(description="Delete file or directory from Cloudflare R2")
    parser.add_argument("path", help="Path to file or directory to delete")
    parser.add_argument("--bucket", "--bucket_name", dest="bucket_name", help="Cloudflare R2 bucket name (overrides CLOUDFLARE_BUCKET_NAME environment variable)")
    args = parser.parse_args()

    try:
        cf = CloudflareR2(bucket_name=args.bucket_name)
        delete(cf, args.path)
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please ensure all required environment variables are set.")


if __name__ == "__main__":
    main()
