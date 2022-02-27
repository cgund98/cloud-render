"""
Initialize AWS client classes.
"""
from typing import Optional

import boto3

from ..creds import load_creds
from ..deploy import StackManager
from ..jobs import JobsController
from ..config import BUCKET_NAME

stack_manager: Optional[StackManager] = None
jobs_controller: Optional[JobsController] = None


def init_jobs_controller() -> JobsController:
    """Initialize the jobs controller with the credentials saved to disk."""

    # Check if controller is already initialized
    global jobs_controller
    if jobs_controller is not None:
        return jobs_controller

    # Initialize controller
    access_key_id, secret_access_key, region = load_creds()
    common_args = dict(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region,
    )

    s3_client = boto3.client(
        "s3",
        **common_args,
    )
    bucket = boto3.resource("s3", **common_args).Bucket(BUCKET_NAME)
    batch_client = boto3.client("batch", **common_args)

    jobs_controller = JobsController(s3_client, bucket, batch_client)

    return jobs_controller


def init_stack_manager() -> StackManager:
    """Initialize the stack manager with the credentials saved to disk."""

    # Check if manager is already initialized
    global stack_manager
    if stack_manager is not None:
        return stack_manager

    # Initialize manager
    access_key_id, secret_access_key, region = load_creds()
    common_args = dict(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region,
    )

    cf_client = boto3.client("cloudformation", **common_args)
    bucket = boto3.resource("s3", **common_args).Bucket(BUCKET_NAME)
    stack_manager = StackManager(cf_client, bucket)

    return stack_manager
