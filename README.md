[![Lint and Build](https://github.com/cgund98/cloud-render/actions/workflows/build.yaml/badge.svg)](https://github.com/cgund98/cloud-render/actions/workflows/build.yaml)
# Cloud Render

> A blender add-on for creating your own private render farm on AWS.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Amazon AWS](https://img.shields.io/badge/Amazon_AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)

Are you stuck working on a potato PC? Want to use your workstation for other tasks while you render? Or maybe you just want to render overnight without falling asleep to coil whine.

If any of those problems seem familiar, you may want to try processing your renders on **your own private render farm**!

Cloud Render is a **free** add-on for blender that enables you to easily deploy a render farm and run your rendering workloads in the cloud (AWS).

### Features
* Render multiple blend files in parallel.
* Run your workloads on up to **80 CPU cores** at once for extremely cheap (<$1/hr).
* Entire process requires no coding or technical experience.
* Full support for compositing workflows with multiple file outputs.

## Getting started

### Installation
Download the latest `zip` file of the add-on from the [releases page](https://github.com/cgund98/cloud-render/releases).

1. Install and enable the zip file like any other add-on via `Edit > Preferences > Add-ons`.
2. Stay on the the Add-ons tab in the Preferences window.

    Expand the "Cloud Render" add-on and click the `Install dependencies` button if you have not done so before.
    
    You may have to run blender as an administrator the first time you do this.
3. You should now see a new panel under `Properties > Render Settings > Cloud Render`. You've installed the add-on!

### Authenticating to AWS
Now that you've installed the add-on, you need to create an AWS account and enter your credentials so the add-on can create your render farm for you.

1. Create an AWS an account. If you need help, follow the [official instructions](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).
2. Create a set of credentials for a service account by following [this guide](./docs/guides/creating-service-account.md).
3. Under the `Cloud Render > AWS Credentials` enter your desired AWS region, access key ID, and secret access key from the previous step.

    Your region is the geographic data center in which your service will operate. For example, `us-east-2` is a data center in Ohio, USA.

    For picking a region, try to pick one of the larger regions, one of: `us-east-1`, `us-east-2`, `us-west-1`, `us-west-2`, `eu-west-1`, `eu-west-2`, `ap-southeast-1`, `ap-southeast-2`. See a full list of regions [here](https://awsregion.info/).

### Manage your render farm
You should be all set to deploy your private render farm! Managing farms is done through the `Cloud Render > Render Farm` panel.

If the render farm status is `UNKNOWN`, simply refresh the farm status with the `Refresh` button.

If the farm's status is `NOT_DEPLOYED`, you can deploy a new farm with the `Deploy` button.

You can shut down a render farm at any time with the `Shut Down` button.

_Note: you will have only one render farm across all your blend files._

### Create a new job
Creating a new render job is quite simple inside the `Cloud Render > Jobs > New` panel.

There is only one option, `Render Animation`. If unchecked, the job will only render the current frame. If checked, it will render the entire animation.

When you are ready, click `Create job`. This will do a few things:
1. Pack all external resources inside your blend file. This is the same as `File > External Data > Pack Resources`.
2. Save the blend file.
3. Upload the blend file to the cloud.
4. For every frame that will be rendered, create a "batch job". Your job will render one frame at a time in parallel.

That's it!

### Manage jobs
You can manage all existing jobs across all blend files in the `Cloud Render > Jobs > Manage` panel.

Use the `Refresh` button to refresh the list of jobs as well as the details of the selected job.

At any time, even when a job is not yet completed, you can pull its output files and save them locally. Do this by selecting an output directory and clicking the `Download Files` button.

*Note: ensure your renders do not write anywhere outside of the same path as the blend file. All render outputs should be under `//`. Anything outside of this path will not be recognized and downloaded.*

Delete the selected job with the `Delete Job` button. This will remove all job files from the cloud permanently.

## FAQ

### What is AWS?
[Amazon Web Services (AWS)](https://aws.amazon.com/what-is-aws/) is a leading cloud platform used by companies around the world. Seriously, AWS powers probably half the internet.

For our purposes, we can just think of them as a "hosting service". Instead of buying PCs ourselves and connecting them to the internet, you can simply rent out machines and storage space from AWS.

You could buy 3 dedicated rendering machines for your office, our you could rent hundreds of servers over the course of a few hours and shut them down when you're finished. You only pay for what you use.

### How much does it cost?
For more details on costs of running render jobs, please see the [pricing guide](./docs/overview/pricing.md).

## Troubleshooting
If you run into any problems using the add-on, please create a [new issue](https://github.com/cgund98/cloud-render/issues/new).

### Deleting render farm manually
If for whatever reason the add-on is not working or you want to be completely sure you aren't being charged for resources that are currently running, you need to delete the AWS resources manually.

This is quite easy. Navigate to the "CloudFormation" service via the search menu. Make sure you have selected the same region in the top right of the window as you entered in the add-on panel. E.g. if you entered `us-east-2`, you should see "Ohio".

In the "Stacks" tab, any resources created by the add-on will have a name starting with `cloud-render-`. If they exist, feel free to delete them. This should remove all resources by Cloud Render.

## Contributing
Have any ideas for new features or improvements? Feel free to create an [issue](https://github.com/cgund98/cloud-render/issues/new), or simply implement the changes yourself!

1. [Fork it](https://github.com/cgund98/cloud-render/fork)
2. Create your feature branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-name`)
5. Create a new Pull Request