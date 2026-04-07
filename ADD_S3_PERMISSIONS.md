# 🔐 Add S3 Permissions to Your AWS User

Your AWS user "augustin" needs S3 permissions to create buckets. Follow these steps:

## Step 1: Open AWS IAM Console
Go to: https://console.aws.amazon.com/iam/

## Step 2: Click "Users" (Left Sidebar)

## Step 3: Find and Click "augustin"

## Step 4: Click "Add Permissions" Button
- Select: "Attach policies directly"

## Step 5: Search for "S3" Policy
In the search box, type: `S3`

You should see policies like:
- AmazonS3FullAccess
- AmazonS3ReadOnlyAccess

## Step 6: Select "AmazonS3FullAccess"
Check the box next to: ✓ AmazonS3FullAccess

This gives your user full S3 access.

## Step 7: Click "Add Permissions"

## Step 8: Wait 1-2 minutes for permissions to take effect

## Step 9: Come back and tell me when done!
Then I'll create your S3 bucket.
