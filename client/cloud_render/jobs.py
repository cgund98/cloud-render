"""
Logic pertaining to creating and managing jobs.
"""

from typing import Dict, Optional, List, Any
from datetime import datetime
import json
import random
import string
import pathlib

from mypy_boto3_s3 import S3Client
from mypy_boto3_batch import BatchClient
from pydantic import BaseModel
import botocore
import typer

from config import (
    JOBS_STATE_FILE,
    BUCKET_NAME,
    JOB_DEF_CPU,
    JOB_DEF_GPU,
    JOB_QUEUE_CPU,
    JOB_QUEUE_GPU,
    STATUS_ERROR,
    STATUS_SUCCEEDED,
    STATUS_RUNNING,
)
from utils import DateTimeEncoder

# Maximum number of times to try and generate a new unique ID before raising an error
MAX_TRIES = 5


class BatchJob(BaseModel):
    """
    Data model of an individual AWS job.
    A Job will have 1 BatchJob for every frame in the animation.
    """

    batch_id: str
    name: str
    status: Optional[str]
    frame: int


class Job(BaseModel):
    """Data model of a render job"""

    job_id: str
    creation_date: datetime
    children: Dict[int, BatchJob]
    start_frame: int
    end_frame: int
    gpu: bool
    file_name: str
    status: Optional[str]


class JobsController:
    """The JobsController manages jobs"""

    s3_client: S3Client
    bucket: Any
    batch_client: BatchClient
    state: Dict[str, Job]

    def __init__(self, s3_client: S3Client, bucket: Any, batch_client: BatchClient):
        self.s3_client = s3_client
        self.bucket = bucket
        self.batch_client = batch_client
        self.state = {}

    def _load_state(self):
        """Load jobs state from S3, initialize empty dict if not found"""

        read_state = {}

        try:
            obj = self.s3_client.get_object(Bucket=BUCKET_NAME, Key=JOBS_STATE_FILE)
            body = obj["Body"].read().decode("utf-8")
            read_state = json.loads(body)
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] != "NoSuchKey":
                raise error

        self.state = {key: Job.parse_obj(val) for key, val in read_state.items()}

    def _persist_state(self) -> None:
        """Persist the jobs state to S3"""

        state_dict = {key: val.dict() for key, val in self.state.items()}
        serialized = bytes(json.dumps(state_dict, cls=DateTimeEncoder), "utf-8")

        self.s3_client.put_object(Bucket=BUCKET_NAME, Key=JOBS_STATE_FILE, Body=serialized)

    def _generate_id(self) -> str:
        """Generate a unique Job ID"""

        i = 0
        while i < MAX_TRIES:
            job_id = "".join(random.choices(string.ascii_lowercase, k=4))

            if job_id not in self.state:
                return job_id

            i += 1

        raise Exception("Unable to generate ID.")

    def _create_batch_jobs(self, job_id: str, start_frame: int, end_frame: int, gpu: bool) -> Dict[int, BatchJob]:
        """Create batch jobs for a render job"""

        batch_jobs = {}

        # Pick job definition and queue
        job_def, job_queue = JOB_DEF_CPU, JOB_QUEUE_CPU
        if gpu:
            job_def, job_queue = JOB_DEF_GPU, JOB_QUEUE_GPU

        # Create a batch job for each frame
        for frame_num in range(start_frame, end_frame + 1):
            name = f"render-job-{job_id}-frame-{frame_num}"
            params = dict(frame=str(frame_num), job=job_id)

            # Make request
            response = self.batch_client.submit_job(
                jobName=name,
                jobQueue=job_queue,
                jobDefinition=job_def,
                parameters=params,
            )

            # Create pydantic model
            batch_job = BatchJob(batch_id=response["jobId"], name=response["jobName"], frame=frame_num)
            batch_jobs[frame_num] = batch_job

            typer.echo(f"Created batch job {batch_job.name}")

        return batch_jobs

    def create_job(self, blend_path: str, start_frame: int, end_frame: int, gpu: bool = False) -> Job:
        """
        Create a new job. That process composes of several steps:
        1. Generate a unique ID
        2. Upload blend file to S3
        3. Create AWS Batch jobs

        :param blend_path: Path to the blend file to upload.
        """

        # Reload state
        self._load_state()

        # Generate ID
        typer.echo("Generating unique ID...")
        job_id = self._generate_id()

        # Upload blend file to S3
        typer.echo("Uploading blend file to S3...")
        obj_key = f"jobs/{job_id}/main.blend"
        self.s3_client.upload_file(Filename=blend_path, Bucket=BUCKET_NAME, Key=obj_key)

        # Create AWS Batch jobs
        typer.echo("Creating batch jobs...")
        batch_jobs = self._create_batch_jobs(job_id, start_frame, end_frame, gpu)

        # Create pydantic model
        job = Job(
            job_id=job_id,
            creation_date=datetime.now(),
            children=batch_jobs,
            start_frame=start_frame,
            end_frame=end_frame,
            gpu=gpu,
            file_name=pathlib.Path(blend_path).name,
            status=STATUS_RUNNING,
        )
        self.state[job.job_id] = job

        # Persist state
        self._persist_state()

        typer.echo(f"Created render job with id: {job.job_id}")

        return job

    def list_jobs(self) -> List[Job]:
        """List available jobs in descending order of their creation date"""

        # Reload state
        self._load_state()

        # Refresh job statuses
        for job in self.state.values():
            if job.status not in (STATUS_SUCCEEDED, STATUS_ERROR):
                self.state[job.job_id] = self._refresh_job(job)

        # Persist state
        self._persist_state()

        # Parse jobs
        jobs = list(self.state.values())
        jobs = sorted(jobs, key=lambda job: job.creation_date, reverse=True)

        return jobs

    def _refresh_children(self, children: Dict[int, BatchJob]) -> Dict[int, BatchJob]:
        """Refresh a set of batch jobs by querying the AWS API"""

        job_ids = [job.batch_id for job in children.values()]

        id_maps = {val.batch_id: key for key, val in children.items()}

        # Iterate over chunks of 100 jobs maximum (limited by AWS)
        cur_chunk, chunk_size = 0, 100
        while cur_chunk < (len(children) // chunk_size) + 1:
            chunk_start, chunk_end = cur_chunk * chunk_size, (cur_chunk + 1) * chunk_size

            response = self.batch_client.describe_jobs(jobs=job_ids[chunk_start:chunk_end])

            for obj in response["jobs"]:
                children[id_maps[obj["jobId"]]].status = obj["status"]

            cur_chunk += 1

        return children

    def _refresh_job(self, job: Job) -> Job:
        """Refresh a job by querying its children and checking it's status"""

        # Refresh children
        job.children = self._refresh_children(job.children)

        # Determine parent job's status
        running = False
        ran_into_error = False
        for batch_job in job.children.values():
            if batch_job.status == "FAILED":
                ran_into_error = True

            if batch_job.status in ("SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING"):
                running = True

        if not running and not ran_into_error:
            job.status = STATUS_SUCCEEDED
        elif not running and ran_into_error:
            job.status = STATUS_ERROR
        else:
            job.status = STATUS_RUNNING

        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Fetch a job from state by its job ID"""

        # Refresh state
        self._load_state()

        # Return None if not found
        if job_id not in self.state:
            return None

        job = self.state[job_id]

        # Update job
        job = self._refresh_job(job)

        # Persist state
        self.state[job_id] = job
        self._persist_state()

        return job

    def delete_job(self, job: Job) -> None:
        """Cancel a job and remove it from the state"""

        # Refresh state
        self._load_state()

        # Cancel children
        typer.echo("Cancelling batch jobs...")
        for batch_job in job.children.values():
            self.batch_client.cancel_job(jobId=batch_job.batch_id, reason="Canceled by user.")

        # Remove S3 directory
        typer.echo("Removing artifacts...")
        self.bucket.objects.filter(Prefix=f"jobs/{job.job_id}").delete()

        # Remove job from state
        typer.echo("Delete job from state...")
        del self.state[job.job_id]

        # Persist state
        self._persist_state()
