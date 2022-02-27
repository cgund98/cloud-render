# Creating an AWS service account

Creating a service account is probably the most difficult part of the installation process, but have no worries! This guide will walk you through the process step-by-step.

The steps can be summarized with:
1. Logging into the AWS console.
2. Navigating to the Identity and Access Management (IAM) dashboard.
3. Creating a new IAM policy
4. Creating a new user (service account)

## Process

### Logging into the AWS console.
Start by logging in to the AWS console. If you haven't created an account yet, you can find the official instructions on that [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).

### Navigating to the IAM dashboard
We need to navigate to the Identity and Access Management (IAM) dashboard. Simply type IAM in the search box and select the "IAM" service from the dropdown.

### Creating a new IAM policy
We'll start with creating a new IAM policy. What this will do is tell AWS what permissions we want to give our service account. We wouldn't want to give the add-on free reign of our entire account, would we?

1. Click the "Policies" tab on the left-hand side of the window.
2. Click the "Create Policy" button to create a new policy.
3. Instead of using the visual editor, select the JSON tab and copy and paste the following contents:
    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "cloudformation:*"
                ],
                "Resource": "*",
                "Effect": "Allow"
            },
            {
                "Condition": {
                    "ForAnyValue:StringEquals": {
                        "aws:CalledVia": [
                            "cloudformation.amazonaws.com"
                        ]
                    }
                },
                "Action": "*",
                "Resource": "*",
                "Effect": "Allow"
            },
            {
                "Action": "s3:*",
                "Resource": "arn:aws:s3:::cdktoolkit-stagingbucket-*",
                "Effect": "Allow"
            },
            {
                "Action": "s3:*",
                "Resource": "arn:aws:s3:::cloud-render-*",
                "Effect": "Allow"
            },
            {
                "Action": "batch:*",
                "Resource": "*",
                "Effect": "Allow"
            }
        ]
    }
    ```
    If you aren't comfortable with those permissions, feel free to tweak them to be more restrictive.
4. Select "Next: Tags" to move on. You can add any tags here if you like, but you don't have to.
5. Select "Next: Review" to move on again. Give the policy a memory name, I will use `CloudRenderSvcPolicy` as an example. Give it a helpful description like `Policy used by the Cloud Render service account. Gives access to CloudFormation, Batch, and S3`.
6. Click "Create policy" to finally create the policy.

You've now created the IAM policy that our service account will use! Woohoo!

### Creating a new user (service account)
Now we need to actually create the service account that the add-on will authenticate to AWS with.
At the end of this step, you will have a set of AWS credentials that you can use to log in with inside the add-on.

1. Navigate to the "Users" tab on the left side of the window.
2. Click "Add users" to create a new user.
3. Pick a memorable user name. I will use `CloudRenderSvc` to note that this is the cloud-render service account.
4. Select the "Access key - Programmatic access" option for a credential type.
5. Click "Next: Permissions" to move on. Select "Attach existing policies directly" and search for the policy we created in the previous step, e.g. `CloudRenderSvcPolicy`. Make sure you select it with the checkbox to the left of the policy name.
6. Select "Next: Tags". Add any tags if you feel like it.
7. Select "Next: Review" to reach the final review stage. Ensure that the all the user details match what we selected previously. You should see the user name, access typer, and also the policy we selected.
8. Finally click "Create user" to create the account. You should see a success screen now, where you have the chance to save the account's credentials.
9. *IMPORTANT*: Save these credentials somewhere safe. If you lose them, you may have to create another service account (but you can reuse the policy from earlier).
10. Enter the credentials in the "Properties > Render Settings > Cloud Render > Credentials" panel. If you lose track of which credential is which, usually Secret Access Key is the longer of the two.

### Congratulations!
You should be all ready to start using the add-on now! Try creating a new render farm deployment now.

## FAQ
### What is a service account?
Plainly put, a service account is a user account made specifically to be used programatically. You wouldn't actually log in with a service account, but some piece of code (e.g. this add-on) would do so.
