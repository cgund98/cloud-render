# Requesting access to GPU spot instances

## What are instances?
Our renders will run on virtual machine instances, which you can think of as servers that AWS spins up on demand for us.

An instance type is essentially a "flavor" of machine that we want to use. Different instance types have different resources, e.g. some have 4 CPUs and 16Gb of memory, others may have 2CPUs and 32Gb of memory, and others have GPUs. 

What instance type you use depends on your use case, but for rendering we mainly care about compute power, so CPUs and especially GPUs.

## Instance limits
AWS sets limits on the number of spot instances any account can request. This is to prevent their infrastructure from being overwhelmed, as one person can't simply create an account, spin up 1000 nodes and mine cryptocurrency as an example.

You can view your account's limits in the "Limits" page of the EC2 dashboard.

## Requesting increase in GPU quotas
Unfortunately, the limit on requests GPU instances are 0 by default, so you will have to request a limit increase. At the time of writing this, I was unable to have my limit increases approved :(. It seems even AWS can't get ahold of enough GPUs in these shortages.

1. Open up https://console.aws.amazon.com/support/home#/case/create?issueType=service-limit-increase&limitType=service-code-ec2-spot-instances.
2. You should now see a form for requesting a limit increase. We will make two requests here on for `G` instances and another for `P`. For each request:
    1. Select the region you are using for your deployment. E.g. `US West (Oregon)`.
    2. Select the corresponding instance type, either `G` or `P`.
    3. Set a new CPU limit value of `16`. On average, most GPU instances have about 4 CPUs per GPU, so this should be enough for 4 GPU instances.
    4. Click "Add another request" and repeat the previous three steps for `P` instance types (assuming you just completed a request for `G` instances).
3. Fill out a brief description of the use case. You can write something about using it to process your visual effects workloads or something like that.
4. Select your prefered contact option and click Submit!
5. Simply wait and hope your request will be approved.