"""
Blender UI base classes that will be inhereted by other UI elements
"""
from os import access
import boto3

from cloud_render.creds import load_creds
from cloud_render.deploy import StackManager
from cloud_render.jobs import JobsController

class CloudRender_BasePanel:
    """Base class for base panels"""

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"


def load_jobs_controller() -> JobsController:
    """Load the jobs controller with the credentials saved to disk."""

    access_key_id, secret_access_key = load_creds()

    s3_client = boto3.client("s3", aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    bucket = boto3.resource("s3").Bucket(BUCKET_NAME)
    batch_client = boto3.client("batch")
    jobs_controller = JobsController(s3_client, bucket, batch_client)