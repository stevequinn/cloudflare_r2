import os
import hashlib
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import argparse


class CloudflareR2:
    def __init__(self):
        self.account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        self.access_key_id = os.environ.get('CLOUDFLARE_ACCESS_KEY_ID')
        self.secret_access_key = os.environ.get('CLOUDFLARE_SECRET_ACCESS_KEY')
        self.bucket_name = os.environ.get('CLOUDFLARE_BUCKET_NAME')
        self.endpoint_url = os.environ.get('CLOUDFLARE_ENDPOINT')

        if not all([self.account_id, self.access_key_id, self.secret_access_key, self.bucket_name, self.endpoint_url]):
            raise ValueError("Missing required environment variables")

        self.s3 = boto3.client('s3',
                               # endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
                               endpoint_url=self.endpoint_url,
                               aws_access_key_id=self.access_key_id,
                               aws_secret_access_key=self.secret_access_key,
                               region_name='auto'
                               )

    def calculate_md5(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def file_exists(self, key):
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def upload_file(self, file_path, relative_path):
        try:
            key = relative_path.replace("\\", "/")
            local_md5 = self.calculate_md5(file_path)

            if self.file_exists(key):
                remote_obj = self.s3.head_object(
                    Bucket=self.bucket_name, Key=key)
                remote_md5 = remote_obj['ETag'].strip('"')
                if local_md5 == remote_md5:
                    print(
                        f"File {key} already exists and is up to date. Skipping.")
                    return
                else:
                    print(f"File {key} exists but has changed. Updating...")
            else:
                print(f"Uploading new file {key}...")

            with open(file_path, 'rb') as file:
                self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=file)
            print(f"Successfully uploaded {key}")
        except ClientError as e:
            print(f"Error uploading {key}: {str(e)}")

    def upload(self, path, base_path):
        if os.path.isfile(path):
            relative_path = os.path.relpath(
                path, start=os.path.dirname(base_path))
            self.upload_file(path, relative_path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(
                        file_path, start=os.path.dirname(base_path))
                    self.upload_file(file_path, relative_path)
        else:
            print(f"Invalid path: {path}")

    def delete(self, path):
        """
        Delete a file or folder within a Cloudflare R2 bucket.

        :param path: The path of the file or folder to delete (e.g. "path/to/file" or "path/to/folder")
        """
        # bucket = self.s3.get_bucket(self.bucket_name)

        # Split the path into its components
        path_components = path.split('/')

        # If the path ends with a slash, it's a folder
        if path_components[-1] == '':
            # Remove the trailing slash
            path_components.pop()

            # Create the folder path
            folder_path = '/'.join(path_components)

            # Get the list of objects in the bucket
            objects = self.s3.list_objects(Bucket=self.bucket_name, Prefix=folder_path)

            # # Iterate through the objects and delete them
            for obj in objects['Contents']:
                print(f'Deleting {obj["Key"]}')
                self.s3.delete_object(Bucket=self.bucket_name, Key=obj['Key'])

            # Delete the folder itself (note: this will also delete any contents)
            self.s3.delete_object(Bucket=self.bucket_name,
                                  Key=folder_path + '/')
        else:
            # It's a file, so just delete it
            print(f'Deleting {path}')
            self.s3.delete_object(Bucket=self.bucket_name, Key=path)


def main():
    parser = argparse.ArgumentParser(
        description="Upload file or directory to Cloudflare R2")
    parser.add_argument("path", help="Path to file or directory to upload or delete")
    parser.add_argument("-b", "--base_path", required=False,
                        help="Base path to use as the root in R2")
    parser.add_argument("-u", "--upload", action='store_true',
                        default=False, help="Upload directory or file")
    parser.add_argument("-d", "--delete", action='store_true',
                        default=False, help="Delete directory or file specified by path")
    args = parser.parse_args()

    try:
        load_dotenv()
        uploader = CloudflareR2()

        if args.upload and args.base_path:
            uploader.upload(args.path, args.base_path)
        elif args.delete:
            uploader.delete(args.path)
        else:
            print('Please choose to upload to delete')
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please ensure all required environment variables are set.")


if __name__ == "__main__":
    main()
