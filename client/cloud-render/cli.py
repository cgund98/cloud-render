"""
CLI entrypoint for the cloud-render client. This is helpful for testing without using the blender UI itself.
"""

import typer
import boto3

from deploy import StackManager

# Init typer
app = typer.Typer()

# Initialize stack manager
cf_client = boto3.client("cloudformation")
stack_manager = StackManager(cf_client)


# Define commands
@app.command()
def deploy():
    """Deploy the CloudFormation stack"""

    stack_manager.create_or_update()


@app.command()
def status():
    """Check the status of the CloudFormation stack"""

    stack = stack_manager.get()

    if stack is None:
        typer.echo("Stack not currently deployed.")

    elif stack.status == "CREATE_COMPLETE":
        typer.echo("Stack is ready!")

    else:
        typer.echo(f"Stack deployed with status: {stack.status}.")


@app.command()
def destroy():
    """Destroy the CloudFormation stack"""

    stack = stack_manager.get()

    if stack is None:
        typer.echo("Stack not currently deployed.")

    else:
        stack_manager.delete()


if __name__ == "__main__":
    app()
