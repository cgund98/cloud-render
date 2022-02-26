"""
Application configuration.
"""

from os import path
from pathlib import Path
import configparser

# Read config file
script_path = path.dirname(path.realpath(__file__))
config = configparser.ConfigParser()
config.read(str(Path(script_path) / Path("config.ini")))

# Deployment type (E.g. "dev", "test", "prod")
DEPLOYMENT = config['default']['Deployment']

# Deployment version
VERSION = config['default']['Version']

# Minimum resource requirements
MIN_CPUS = "0"

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