"""
Initialize AWS client classes
"""
from inspect import stack
import boto3

from cloud_render.creds import load_creds
from cloud_render.deploy import Stack, StackManager
from cloud_render.jobs import JobsController
from cloud_render.config import BUCKET_NAME


def init_jobs_controller() -> JobsController:
    """Initialize the jobs controller with the credentials saved to disk."""

    access_key_id, secret_access_key, region = load_creds()
    common_args = dict(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, region_name=region)

    s3_client = boto3.client("s3", **common_args,)
    bucket = boto3.resource("s3", **common_args).Bucket(BUCKET_NAME)
    batch_client = boto3.client("batch", **common_args)

    jobs_controller = JobsController(s3_client, bucket, batch_client)

    return jobs_controller


def init_stack_manager() -> StackManager:
    """Initialize the stack manager with the credentials saved to disk."""

    access_key_id, secret_access_key, region = load_creds()
    common_args = dict(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, region_name=region)

    cf_client = boto3.client("cloudformation", **common_args)
    stack_manager = StackManager(cf_client)

    return stack_manager