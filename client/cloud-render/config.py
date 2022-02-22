"""
Application configuration.
"""

from os import environ as env

# Deployment type (E.g. "dev", "test", "prod")
DEPLOYMENT = env.get("DEPLOYMENT", "dev")

# Minimum resource requirements
MIN_CPUS = "4"

# Instance Types
GPU_INSTANCE_TYPES = "g4dn,p2,p3"
CPU_INSTANCE_TYPES = "m6i,m5"
