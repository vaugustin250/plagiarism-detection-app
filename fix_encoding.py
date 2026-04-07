import os

# The original file had null bytes appended
# Let's read the good part and remove null bytes

with open('03_streamlit_dashboard.py', 'rb') as f:
    content = f.read()

# Remove null bytes
clean_content = content.replace(b'\x00', b'')

# Write back
with open('03_streamlit_dashboard.py', 'wb') as f:
    f.write(clean_content)

print("✅ Null bytes removed")
print(f"Clean file size: {len(clean_content)} bytes")

# Verify
with open('03_streamlit_dashboard.py', 'rb') as f:
    verify = f.read()
    if b'\x00' in verify:
        print("❌ Still has null bytes")
    else:
        print("✅ File is clean - no more null bytes")
