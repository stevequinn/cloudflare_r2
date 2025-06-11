"""
Cloudflare R2 Main Script

This script provides a unified interface to upload or delete files and directories in Cloudflare R2 storage.
It can be run as a standalone script.

Usage:
    As a script:
        python cloudflare_r2_main.py -u <path> -b <base_path>  # For upload
        python cloudflare_r2_main.py -d <path>                 # For delete
"""
import argparse
from cloudflare_r2 import CloudflareR2
from cloudflare_r2_delete import delete
from cloudflare_r2_upload import upload

def main() -> None:
    """
    Main function to handle command-line arguments and initiate the appropriate process.
    """
    parser = argparse.ArgumentParser(description="Manage files in Cloudflare R2")
    parser.add_argument("path", help="Path to file or directory to upload or delete")
    parser.add_argument("-b", "--base_path", help="""Base path to use as the root in R2.
                        The local directory structure will be mirrored in R2 from here down. (required for upload)
                        IMPORTANT: This is the local base path on your file system, not the R2 bucket path.
                        Most likely this will be ../whatsworn-cdn/
                        """)
    parser.add_argument("-u", "--upload", action='store_true', help="Upload directory or file")
    parser.add_argument("-d", "--delete", action='store_true', help="Delete directory or file specified by path")
    args = parser.parse_args()

    try:
        r2: CloudflareR2 = CloudflareR2()

        if args.upload and args.base_path:
            upload(r2, args.path, args.base_path)
        elif args.delete:
            delete(r2, args.path)
        else:
            print('Please choose to upload (-u) or delete (-d)')
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please ensure all required environment variables are set.")


if __name__ == "__main__":
    main()
