import os
import shutil
import subprocess
import zipfile

# Step 1: Create lambda package directory
if os.path.exists('lambda_function_package'):
    shutil.rmtree('lambda_function_package')
os.makedirs('lambda_function_package')

# Step 2: Copy handler and rename
shutil.copy('02_lambda_handler.py', 'lambda_function_package/lambda_function.py')

# Step 3: Copy minimal requirements
with open('lambda_function_package/requirements.txt', 'w') as f:
    f.write("""boto3==1.26.137
psycopg2-binary==2.9.6
pinecone-client==2.2.3
PyPDF2==3.0.1
requests==2.31.0
python-dotenv==1.0.0
""")

print("✅ Step 1: Package structure created")
print(f"   Files: {os.listdir('lambda_function_package')}")

# Step 4: Install dependencies
os.chdir('lambda_function_package')
subprocess.run(['pip', 'install', '-r', 'requirements.txt', '-t', '.', '--quiet'], check=True)
os.chdir('..')

print("✅ Step 2: Dependencies installed")

# Step 5: Create ZIP file
def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, path)
            ziph.write(file_path, arcname)

with zipfile.ZipFile('lambda_function.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir('lambda_function_package', zipf)

zip_size = os.path.getsize('lambda_function.zip') / (1024*1024)
print(f"✅ Step 3: ZIP file created")
print(f"   File: lambda_function.zip")
print(f"   Size: {zip_size:.1f} MB")

print("\n✅ Lambda package ready for upload!")
print("   Location: lambda_function.zip")
