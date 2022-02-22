"""
AWS CDK stack
"""

from aws_cdk import core as cdk

from .deployment import RenderBackend

app = cdk.App()
backend = RenderBackend()

app.synth()