"""
Cloudflare R2 S3 Instance Class

Environment Variables:
    CLOUDFLARE_ACCOUNT_ID: Your Cloudflare account ID
    CLOUDFLARE_ACCESS_KEY_ID: Your Cloudflare access key ID
    CLOUDFLARE_SECRET_ACCESS_KEY: Your Cloudflare secret access key
    CLOUDFLARE_BUCKET_NAME: Your Cloudflare R2 bucket name
    CLOUDFLARE_ENDPOINT: Your Cloudflare R2 endpoint URL
"""
import os
from typing import Optional
import boto3
from botocore.client import BaseClient
from dotenv import load_dotenv


class CloudflareR2:
    """
    Cloudflare R2 S3 instance class
    """

    def __init__(self) -> None:
        """
        Initialize the CloudflareR2 with necessary credentials and configurations.
        Raises ValueError if any required environment variables are missing.
        """
        load_dotenv()
        self._account_id: Optional[str] = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        self._access_key_id: Optional[str] = os.environ.get('CLOUDFLARE_ACCESS_KEY_ID')
        self._secret_access_key: Optional[str] = os.environ.get('CLOUDFLARE_SECRET_ACCESS_KEY')
        self._bucket_name: Optional[str] = os.environ.get('CLOUDFLARE_BUCKET_NAME')
        self._endpoint_url: Optional[str] = os.environ.get('CLOUDFLARE_ENDPOINT')

        if not all([self._account_id, self._access_key_id, self._secret_access_key,
                    self._bucket_name, self._endpoint_url]):
            raise ValueError("Missing required environment variables")

        self._s3: BaseClient = boto3.client('s3',
                                            endpoint_url=self._endpoint_url,
                                            aws_access_key_id=self._access_key_id,
                                            aws_secret_access_key=self._secret_access_key,
                                            region_name='auto')

    @property
    def s3(self) -> BaseClient:
        """
        S3 Object Getter
        """
        return self._s3

    @property
    def bucket_name(self) -> str:
        """
        Bucket Name Getter
        """
        return self._bucket_name
