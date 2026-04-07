# 🔒 FIX RDS SECURITY GROUP

Your RDS security group is blocking connections. Follow these steps to fix it.

---

## Step 1: Open RDS Console
Go to: https://console.aws.amazon.com/rds/

---

## Step 2: Find Your Database
Click on: "plagiarism-db"

---

## Step 3: Find Security Group
Scroll down to "Connectivity & security"

You'll see:
```
VPC security groups: plagiarism-db-sg (sg-xxxxxxx)
```

Click on the security group ID (sg-xxxxxxx)

---

## Step 4: Edit Inbound Rules
You're now in the EC2 Security Groups console

Find the "Inbound rules" section

Click "Edit inbound rules" button

---

## Step 5: Add Rule for PostgreSQL

Click "Add rule"

Fill in:
```
Type:        PostgreSQL
Protocol:    TCP
Port range:  5432
Source:      0.0.0.0/0 (Allow from anywhere)
```

Click "Save rules"

---

## Step 6: Wait 1-2 Minutes

The rules take effect after a moment.

---

## ✅ When Done

Tell me and I'll test the connection again!
