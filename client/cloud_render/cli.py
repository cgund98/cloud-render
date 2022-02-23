"""
CLI entrypoint for the cloud-render client. This is helpful for testing without using the blender UI itself.
"""
import os

import typer
import boto3

from deploy import StackManager
from jobs import JobsController

# Init typer
app = typer.Typer()

# Initialize stack manager
cf_client = boto3.client("cloudformation")
stack_manager = StackManager(cf_client)

# Initialize jobs controller
s3_client = boto3.client("s3")
batch_client = boto3.client("batch")
jobs_controller = JobsController(s3_client, batch_client)


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
    if not os.path.exists(blend_path) or blend_path.split('.')[-1] != "blend":
        typer.echo(f"No blend file found at path '{blend_path}'")
        typer.Exit(1)

    # Create job
    jobs_controller.create_job(blend_path, start_frame, end_frame, gpu)


@app.command()
def list_jobs():
    """List jobs in state."""

    jobs = jobs_controller.list_jobs()

    typer.echo("ID\tSTART\tEND\tSTATUS\t\tFILE_NAME")
    for job in jobs:
        typer.echo(f"{job.job_id}\t{job.start_frame}\t{job.end_frame}\t{job.status.ljust(10)}\t{job.file_name}")


if __name__ == "__main__":
    app()
