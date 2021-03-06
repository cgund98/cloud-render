"""
CLI entrypoint for the cloud-render client. This is helpful for testing without using the blender UI itself.
"""
import os

import typer
import boto3

from .deploy import StackManager
from .jobs import JobsController
from .config import BUCKET_NAME

# Init typer
app = typer.Typer()

# Initialize stack manager
cf_client = boto3.client("cloudformation")
bucket = boto3.resource("s3").Bucket(BUCKET_NAME)
stack_manager = StackManager(cf_client, bucket)

# Initialize jobs controller
s3_client = boto3.client("s3")
batch_client = boto3.client("batch")
jobs_controller = JobsController(s3_client, bucket, batch_client)


# Define commands
@app.command()
def deploy():
    """Deploy the CloudFormation stack."""

    stack_manager.create_or_update()


@app.command()
def status():
    """Check the status of the CloudFormation stack."""

    stack = stack_manager.get()

    if stack is None:
        typer.echo("Stack not currently deployed.")

    elif stack.status in ("CREATE_COMPLETE", "UPDATE_COMPLETE"):
        typer.echo("Stack is ready!")

    else:
        typer.echo(f"Stack deployed with status: {stack.status}.")


@app.command()
def destroy():
    """Destroy the CloudFormation stack."""

    stack = stack_manager.get()

    if stack is None:
        typer.echo("Stack not currently deployed.")

    else:
        stack_manager.delete()


@app.command()
def create_job(
    blend_path: str = typer.Argument(..., help="Path to blend file to upload"),
    start_frame: int = typer.Option(0, help="Starting frame."),
    end_frame: int = typer.Option(0, help="Starting frame."),
    gpu: bool = typer.Option(False, help="Use GPU or not"),
):
    """Create a new render job."""

    # Ensure blend file is valid
    if not os.path.exists(blend_path) or blend_path.split(".")[-1] != "blend":
        typer.echo(f"No blend file found at path '{blend_path}'")
        typer.Exit(1)

    # Create job
    jobs_controller.create_job(blend_path, start_frame, end_frame, gpu)


@app.command()
def list_jobs():
    """List jobs in state."""

    jobs = jobs_controller.list_jobs()

    typer.echo("ID\tCREATED_AT\t\t\tSTART\tEND\tSTATUS\t\tFILE_NAME")
    for job in jobs:
        typer.echo(
            f"{job.job_id}\t{job.creation_date}\t{job.start_frame}\t"
            f"{job.end_frame}\t{job.status.ljust(10)}\t{job.file_name}"
        )


@app.command()
def describe_job(job_id: str = typer.Argument(...)):
    """Fetch details on a specific job"""

    job = jobs_controller.get_job(job_id)

    if job is None:
        typer.echo(f"No job found with id: {job_id}", color=typer.colors.RED)

    typer.echo(f"Job ID: {job.job_id}")
    typer.echo(f"File name: {job.file_name}")
    typer.echo(f"Status: {job.status}")
    typer.echo(f"Created at: {job.creation_date}")

    if job.completion_date is not None:
        duration = (job.completion_date - job.creation_date).total_seconds() // 60
        typer.echo(f"Duration: {duration} minutes")

    typer.echo(f"Frames: {job.start_frame}-{job.end_frame}")

    typer.echo("\nBatch Jobs:")
    typer.echo("FRAME\tSTATUS\t\tJOB_NAME")
    for batch_job in job.children.values():
        typer.echo(f"{batch_job.frame}\t{batch_job.status.ljust(10)}\t{batch_job.name}")


@app.command()
def delete_job(job_id: str = typer.Argument(...)):
    """Cancel and delete a specific job"""

    job = jobs_controller.get_job(job_id)

    if job is None:
        typer.echo(f"No job found with id: {job_id}", color=typer.colors.RED)

    jobs_controller.delete_job(job)


if __name__ == "__main__":
    app()
