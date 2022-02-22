from typing import Any

from aws_cdk import (
    aws_ec2 as ec2, 
    aws_batch_alpha as batch,
    aws_ecs as ecs,
    Stack, CfnOutput
)
from constructs import Construct


def wrap_env(name: str, env: str) -> str:
    """Helper method that will wrap an object name with the environment"""

    return f"{name}-{env}"


class RenderBackend(Stack):
    """
    AWS CDK class representing our cloud-render backend deployment.
    """
    
    def __init__(
        self,
        scope: Construct,
        id_: str,
        env: str,
        version: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, id_, **kwargs)

        # Create S3 bucket
        bucket_name = wrap_env("cloud-render", env)

        # Create the private/public subnet as well as nat/internet gateway
        vpc = ec2.Vpc(self, wrap_env("cloud-render-vpc", env))

        # Create the compute environment
        compute_env = batch.ComputeEnvironment(
            compute_resources=batch.ComputeResources(
                vpc=vpc,
                instance_types=["g4dn.xlarge"],
                minv_cpus=0,
                maxv_cpus=48,
                type=batch.ComputeResourceType.SPOT,
                bid_percentage=0.25,
            ),
            type=batch.ComputeResourceType.SPOT,
            bid_percentage=0.25,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            vpc=vpc,
        )

        # Create Job Queue
        batch_queue = batch.JobQueue(self, wrap_env("cloud-render-job-queue", env))

        # Create Job Definition to render an image
        job_def = batch.JobDefinition(self, wrap_env("cloud-render-job-def", env), 
            job_definition_name=wrap_env("cloud-render-main", env),
            container=batch.JobDefinitionContainer(image=ecs.ContainerImage.from_registry(
                f"cgundlach/cloud-render-server:{version}"), command=["--frame", "Ref::frame", "--bucket", bucket_name, "--job-name", "Ref::jobname"], vcpus=4),

        )