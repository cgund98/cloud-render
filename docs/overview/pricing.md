# Pricing

## Compute
We run our render jobs on special machines called "[spot instances](https://aws.amazon.com/aws-cost-management/aws-cost-optimization/spot-instances/)". Spot instances are heavily discounted (often 70%+ off) with the caveat that they can be shut down at any given time. We need not worry about this as our render jobs will restart if this happens.

### Batch jobs
Cloud Render breaks up render jobs into smaller "batch jobs" that will render individual frames. E.g. a render job of an animation of 120 frames long will create 120 batch jobs. A render job for a single frame will create a single batch job.

Each batch job will use 4 CPU cores and 16GB of memory. By default, the render queue can only use a maximum of 80 CPU cores at a time, so up to 20 frames can be rendered at the same time.

### Scaling
Cloud Render queues have the advantage of scaling up and down as needed, so you only pay for resources you are actively using.

Render queues will scale up to a maximum of 80 CPU cores (m6i, m5 instances).

If only rendering 1-2 frames at a time, the queue will only use 8 CPU cores, which will cost around $0.0838 per Hour. If fully utilizing the render queue of 80 cores, it should cost a maximum of $1/hr.

## Storage
Job files (blend files, render outputs) are stored in a service called [S3](https://aws.amazon.com/s3/).

S3 storage is priced at [$0.023/GB per Month](https://aws.amazon.com/s3/pricing/). E.g. 100GB of job files will cost $2.30 per Month.

When you aren't actively rendering something, you will only pay for S3 storage, where job files are stored.

## Examples

### Example 1
Storage: We will use a maximum of 50GB of storage for the month.

Compute: We have an animation of 120 frames that take an average of 15 minutes per frame to render. We run this job 30 times per month.

| Charges   | Usage     | Rate      | Subtotal      |
|-----------|-----------|-----------|---------------|
| Storage (GB per month) | 50 GB * 1 month = 50 GB-months | $0.023 per GB-month  | 50 GB-months * $0.023 = $1.15 |
| Compute instances | 30 jobs * 120 frames per job * 0.25 hours per frame / 20 frames at a time = 45 hours | $1 per hour | 45 hours * $1 = $45 |
|Total | | | $1.15 + $45 = $46.15 per month |

### Example 2
Storage: We will use a maximum of 100GB of storage for the month.

Compute: We want to render a single image that take an average of 30 minutes to render. We run this job 120 times per month.

| Charges   | Usage     | Rate      | Subtotal      |
|-----------|-----------|-----------|---------------|
| Storage (GB per month) | 100 GB * 1 month = 100 GB-months | $0.023 per GB-month  | 100 GB-months * $0.023 = $2.30 |
| Compute instances | 120 jobs * 1 frame per job * 0.5 hours per frame = 60 hours | $0.0838 per hour | 60 hours * $0.0838 = $5.03 |
| Total | | | $2.30 + $5.03 = $7.33 per month |

## Caution
In order to prevent any unexpected charges, it's recommended you keep an eye on your AWS charges and enable [billing alerts](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html#turning_on_billing_metrics).

### Request refunds
If you somehow find a large sum of unexpected charges, try to get ahold of customer service and request a refund. They are known for being quite generous in this regard.
