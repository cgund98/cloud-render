"""
Application configuration.
"""

from os import environ as env

# Deployment type (E.g. "dev", "test", "prod")
DEPLOYMENT = env.get("DEPLOYMENT", "dev")

# Deployment version
VERSION = env.get("VERSION", "test")

# Minimum resource requirements
MIN_CPUS = "4"

# Instance Types
GPU_INSTANCE_TYPES = "g4dn,p2,p3"
CPU_INSTANCE_TYPES = "m6i,m5"

# Jobs State
JOBS_STATE_FILE = "jobs.state"

# Bucket name
BUCKET_NAME = f"cloud-render-{DEPLOYMENT}"

# Job Definitions
JOB_DEF_CPU = f"{DEPLOYMENT}CloudRenderCpuRender"
JOB_DEF_GPU = f"{DEPLOYMENT}CloudRenderGpuRender"

# Job Queues
JOB_QUEUE_CPU = f"{DEPLOYMENT}CloudRenderCpuJobQueue"
JOB_QUEUE_GPU = f"{DEPLOYMENT}CloudRenderGpuJobQueue"

# Job status
STATUS_RUNNING = "RUNNING"
STATUS_ERROR = "ERROR"
STATUS_SUCCEEDED = "SUCCEEDED"

# AWS Creds
CREDS_FILE_NAME = "creds.json"