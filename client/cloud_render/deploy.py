"""
Logic pertaining to managing the CloudFormation deployment.
"""

from typing import Sequence, Optional, Any
import os

from mypy_boto3_cloudformation import CloudFormationClient
from mypy_boto3_cloudformation.type_defs import ParameterTypeDef
import botocore
import typer

from pydantic import BaseModel

from .config import (
    DEPLOYMENT,
    MIN_CPUS,
    GPU_INSTANCE_TYPES,
    CPU_INSTANCE_TYPES,
    VERSION,
)

# Path of script. Used to locate template.yaml
script_path = os.path.dirname(os.path.realpath(__file__))


class Stack(BaseModel):
    """
    Data model of a CloudRender CloudFormation stack
    """

    name: str
    status: str
    gpu_queue: Optional[str]
    cpu_queue: Optional[str]


class StackManager:
    """The StackManager manages the current CloudFormation stack, our main deployment method."""

    client: CloudFormationClient
    stack_name: str
    bucket: Any
    parameters: Sequence[ParameterTypeDef]

    def __init__(self, client: CloudFormationClient, bucket: Any):
        self.client = client
        self.stack_name = f"cloud-render-{DEPLOYMENT}"
        self.bucket = bucket

        # Stack parameters
        self.parameters = [
            {
                "ParameterKey": "Prefix",
                "ParameterValue": DEPLOYMENT,
                "UsePreviousValue": False,
            },
            {
                "ParameterKey": "Version",
                "ParameterValue": VERSION,
                "UsePreviousValue": False,
            },
            {
                "ParameterKey": "MinimumVCPUs",
                "ParameterValue": MIN_CPUS,
                "UsePreviousValue": False,
            },
            {
                "ParameterKey": "GpuInstanceTypes",
                "ParameterValue": GPU_INSTANCE_TYPES,
                "UsePreviousValue": False,
            },
            {
                "ParameterKey": "CpuInstanceTypes",
                "ParameterValue": CPU_INSTANCE_TYPES,
                "UsePreviousValue": False,
            },
        ]

    @staticmethod
    def _load_template() -> str:
        """Load the CloudFormation template from the file system."""

        with open(f"{script_path}/template.yaml", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        return template

    def update(self) -> None:
        """Update an existing stack."""

        typer.echo(f"Will update existing stack {self.stack_name}...")

        try:
            template = self._load_template()
            self.client.update_stack(
                StackName=self.stack_name,
                TemplateBody=template,
                Capabilities=["CAPABILITY_NAMED_IAM"],
                Parameters=self.parameters,
            )

            typer.echo("Stack updated")

        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Message"] == "No updates are to be performed.":
                typer.echo("Stack already up to date.")

            else:
                raise error

    def create(self) -> None:
        """Create a non-existent stack."""

        typer.echo(f"Will create stack {self.stack_name}...")

        template = self._load_template()
        self.client.create_stack(
            StackName=self.stack_name,
            TemplateBody=template,
            Capabilities=["CAPABILITY_NAMED_IAM"],
            Parameters=self.parameters,
        )

    def create_or_update(self) -> None:
        """Update the stack if it exists, otherwise create it."""

        # Try to fetch the stack
        stack = self.get()

        # Create if it does exist
        if stack is None:
            self.create()

        # Otherwise update
        else:
            self.update()

    def delete(self) -> None:
        """Delete the existing stack."""

        typer.echo(f"Will delete stack {self.stack_name}...")

        # Remove artifacts from bucket
        typer.echo("Removing artifacts...")
        self.bucket.objects.all().delete()

        # Delete cloud formation
        self.client.delete_stack(StackName=self.stack_name)

    def get(self) -> Optional[Stack]:
        """Fetch the current stack from the AWS API."""

        # Query AWS
        try:
            response = self.client.describe_stacks(StackName=self.stack_name)
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ValidationError":
                return None

            raise error

        if len(response["Stacks"]) == 0:
            return None

        # Parse response into a dictionary so Pydantic can read it
        cur_stack = response["Stacks"][0]
        parsed_stack = {
            "name": cur_stack["StackName"],
            "status": cur_stack["StackStatus"],
            "gpu_queue": "",
            "cpu_queue": "",
        }

        # Check if outputs are ready, and add them to parsed stack
        outputs = cur_stack.get("Outputs")
        if outputs:
            for output in outputs:
                if output["OutputKey"] == "GPUQueue":
                    parsed_stack["gpu_queue"] = output["OutputValue"]
                elif output["OutputKey"] == "CPUQueue":
                    parsed_stack["cpu_queue"] = output["OutputValue"]

        return Stack.parse_obj(parsed_stack)
