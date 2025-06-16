# Cloudflare R2 Helper Scripts

This contains upload and delete functionality for Cloudflare R2.

Make sure to copy the `dot.env` file to `.env` and update its values.

## Features

- Upload files and directories to Cloudflare R2
- Delete files and directories from Cloudflare R2
- Support for custom bucket names via command line parameter
- Automatic fallback to environment variable configuration
- MD5 hash comparison to avoid unnecessary uploads
- MIME type detection for proper content types

## Environment Variables

The following environment variables are required:

- `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare account ID
- `CLOUDFLARE_ACCESS_KEY_ID`: Your Cloudflare access key ID
- `CLOUDFLARE_SECRET_ACCESS_KEY`: Your Cloudflare secret access key
- `CLOUDFLARE_BUCKET_NAME`: Your default Cloudflare R2 bucket name
- `CLOUDFLARE_ENDPOINT`: Your Cloudflare R2 endpoint URL

## Usage

### Command Line Interface

All scripts support an optional `--bucket` parameter that overrides the `CLOUDFLARE_BUCKET_NAME` environment variable.

#### Main Script

```bash
# Upload using environment variable bucket
python -m cloudflare_r2 -u /path/to/file -b /base/path

# Upload using custom bucket
python -m cloudflare_r2 -u /path/to/file -b /base/path --bucket my-custom-bucket

# Delete using environment variable bucket
python -m cloudflare_r2 -d /path/to/file

# Delete using custom bucket
python -m cloudflare_r2 -d /path/to/file --bucket my-custom-bucket
```

#### Upload Script

```bash
# Upload using environment variable bucket
python cloudflare_r2_upload.py /path/to/file -b /base/path

# Upload using custom bucket
python cloudflare_r2_upload.py /path/to/file -b /base/path --bucket my-custom-bucket

# Alternative parameter format
python cloudflare_r2_upload.py /path/to/file -b /base/path --bucket_name my-custom-bucket
```

#### Delete Script

```bash
# Delete using environment variable bucket
python cloudflare_r2_delete.py /path/to/file

# Delete using custom bucket
python cloudflare_r2_delete.py /path/to/file --bucket my-custom-bucket

# Alternative parameter format
python cloudflare_r2_delete.py /path/to/file --bucket_name my-custom-bucket
```

### Python Module Usage

```python
from cloudflare_r2 import CloudflareR2
from cloudflare_r2_upload import upload
from cloudflare_r2_delete import delete

# Using environment variable bucket
r2 = CloudflareR2()

# Using custom bucket
r2 = CloudflareR2(bucket_name="my-custom-bucket")

# Upload operations
upload(r2, "/path/to/file", "/base/path")

# Delete operations
delete(r2, "/path/to/file")
```

## Bucket Name Priority

The bucket name is determined in the following order:

1. **Command line parameter**: `--bucket` or `--bucket_name`
2. **Environment variable**: `CLOUDFLARE_BUCKET_NAME`

If neither is provided, the script will raise a ValueError.
