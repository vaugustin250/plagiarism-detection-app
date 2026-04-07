# 🗄️ CREATE RDS POSTGRESQL DATABASE

Follow these steps EXACTLY to create your database.

---

## Step 1: Open RDS Console
Go to: https://console.aws.amazon.com/rds/

Click the blue "Create database" button

---

## Step 2: Choose Engine
Under "Engine options" select:
✓ PostgreSQL

Then click "Continue"

---

## Step 3: Choose Template
Under "Templates" select:
✓ Free tier

Then click "Continue"

---

## Step 4: Configure DB Instance Settings

Fill in these exact values:

```
DB instance identifier:      plagiarism-db
Master username:             postgres
Password:                    Plagiarism123!
Confirm password:            Plagiarism123!

DB instance class:           db.t3.micro (MUST be this for free tier)
Storage type:                gp2
Allocated storage:           20 GB
```

---

## Step 5: Configure Connectivity
IMPORTANT: Set these exactly:

```
Publicly accessible:         YES ✓ (Check this box!)
VPC security group:          Create new
Security group name:         plagiarism-db-sg
```

---

## Step 6: Create Database
Click the blue "Create database" button at the bottom

⏳ Wait 5-10 minutes for status to change from "Creating" to "Available"

---

## Step 7: Get Connection Details

1. Go to: https://console.aws.amazon.com/rds/
2. Click on your DB instance "plagiarism-db"
3. Under "Connectivity & security" section, find:
   
   **Endpoint:** plagiarism-db.xxxxx.us-east-1.rds.amazonaws.com

Copy this endpoint (the part after "plagiarism-db." varies)

---

## ✅ When Done

Tell me:
1. Your RDS endpoint (looks like: plagiarism-db.c9akciq32.us-east-1.rds.amazonaws.com)

Then I'll:
- Create database tables
- Create Lambda role
- Deploy everything
