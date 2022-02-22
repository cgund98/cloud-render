"""
Deploy cloudformation template
"""

import os

import boto3

# Path of script
script_path = os.path.dirname(os.path.realpath(__file__))

cf_client = boto3.client("cloudformation")
deployment = "test3"

def main():
    """Entrypoint method"""

    with open(f"{script_path}/../template.yaml", 'r') as f:
        template = f.read()

    stack_name = f"cloud-render-{deployment}"

    parameters = [
        dict(ParameterKey="Prefix", ParameterValue=deployment, UsePreviousValue=False),
        dict(ParameterKey="MinimumVCPUs", ParameterValue="4", UsePreviousValue=False),
        dict(ParameterKey="GpuInstanceTypes", ParameterValue="g4dn,p2,p3", UsePreviousValue=False),
        dict(ParameterKey="CpuInstanceTypes", ParameterValue="m6i,m5", UsePreviousValue=False),
    ]
    cf_client.create_stack(StackName=stack_name,TemplateBody=template, Capabilities=['CAPABILITY_NAMED_IAM'], Parameters=parameters)
    response = cf_client.describe_stacks(StackName=stack_name)
    print(response['Stacks'][0]['StackStatus'])

if __name__ == "__main__":
    main()
