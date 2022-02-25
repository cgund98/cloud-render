"""
Logic pertaining to reading and writing credentials from add-on file system.
"""
from typing import Tuple
import os
import json

from cloud_render.config import CREDS_FILE_NAME

# Script path is where credentials will be saved
script_path = os.path.dirname(os.path.realpath(__file__))
creds_path = f"{script_path}/{CREDS_FILE_NAME}"


def save_creds(aws_access_key_id: str, aws_secret_access_key: str, region: str) -> None:
    """Save credentials to local file system."""

    # Format into JSON
    creds_obj = {
        "AWS_ACCESS_KEY_ID": aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
        "AWS_REGION": region,
    }

    # Write credentials to local file system
    with open(creds_path, "w") as creds_file:
        json.dump(creds_obj, creds_file)


def load_creds() -> Tuple[str, str, str]:
    """Load credentials from local file system"""

    # Check if file exists
    if not os.path.exists(creds_path):
        return None, None

    # Read file
    with open(creds_path, "r") as creds_file:
        creds_obj = json.load(creds_file)

    # Parse individual fields
    aws_access_key_id = creds_obj.get("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = creds_obj.get("AWS_SECRET_ACCESS_KEY", "")
    aws_region = creds_obj.get("AWS_REGION", "")

    return aws_access_key_id, aws_secret_access_key, aws_region


def valid_creds() -> bool:
    """Check that valid credentials are set"""

    # Load from FS
    access_key_id, secret_access_key, aws_region = load_creds()

    # Check if credentials are set
    valid = access_key_id and secret_access_key and aws_region

    return valid