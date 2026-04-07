# 🔐 ADD IAM PERMISSIONS TO YOUR USER

You need to add "IAMFullAccess" permission to create roles.

---

## Step 1: Open IAM Console
Go to: https://console.aws.amazon.com/iam/

---

## Step 2: Click "Users" (Left Sidebar)

---

## Step 3: Click "augustin" (Your Username)

---

## Step 4: Click "Add permissions" Button
Select: "Attach policies directly"

---

## Step 5: Search for IAM Policy
In the search box, type: `IAMFullAccess`

You should see:
- ✓ IAMFullAccess (check this one)

---

## Step 6: Select IAMFullAccess
Click the checkbox next to: ✓ IAMFullAccess

This allows you to create and manage IAM roles.

---

## Step 7: Click "Add permissions" Button

---

## Step 8: Wait 1-2 minutes for permissions to take effect

---

## ✅ Then tell me when done!

I'll then automatically create:
- Lambda IAM role
- Setup API Gateway
- Deploy Lambda function
- Everything else!
