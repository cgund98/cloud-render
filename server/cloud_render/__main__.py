"""
Entrypoint script for the server renderer image.
"""

import subprocess
import os

from pathlib import Path
import typer
import boto3

s3 = boto3.client("s3")


def pull_blend(job_name: str, bucket_name: str) -> str:
    """Pull a job's blend file from S3"""

    job_path = f"/cache/{job_name}"
    out_name = f"{job_path}/main.blend"

    # Create job path in cache dir if not exists
    if not os.path.exists(job_path):
        os.mkdir(job_path)

    # Pull file if not found locally
    if not os.path.exists(out_name):
        s3.download_file(bucket_name, f"jobs/{job_name}/main.blend", out_name)

    return out_name


def save_results(job_name: str, bucket_name: str) -> int:
    """Save a job's output to S3"""

    job_path = f"/cache/{job_name}"

    # Iterate over every file in the job directory
    count = 0
    for path in Path(job_path).rglob("*"):

        # Ensure target is a file
        if path.is_file() and path.name != "main.blend":
            typer.echo(f"Uploading file {path}...")

            rel_path = str(path).split(job_path + "/")[1]
            s3.upload_file(str(path), bucket_name, f"jobs/{job_name}/{rel_path}")

            count += 1

    return count


def main(
    job_name: str = typer.Argument(
        ..., help="Name of the blend file to attempt to render"
    ),
    frame: int = typer.Option(..., help="Framer number to render"),
    bucket_name: str = typer.Option(
        ..., help="Name of the S3 bucket to use for storage"
    ),
) -> None:
    """Entrypoint method"""

    typer.echo(f"Will render job {job_name} on frame #{frame}.")

    # Pull blend file from S3
    typer.echo("Pulling blend file from S3...")
    blend_path = pull_blend(job_name, bucket_name)

    # Run blender
    typer.echo("Rendering...")

    job_path = f"/cache/{job_name}"
    subprocess.run(
        ["blender", "-b", blend_path, "-o", "./out/frame_####", "-f", str(frame)],
        check=True,
        cwd=job_path,
    )

    # Copy results back to S3
    save_count = save_results(job_name, bucket_name)
    typer.echo(f"Copied {save_count} files to bucket.")

    # All done
    typer.echo("Rendered image successfully!", color=typer.colors.GREEN)


if __name__ == "__main__":
    typer.run(main)
