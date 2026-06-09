# Create dummy files for testing uploads
import os
from pathlib import Path

upload_dir = Path("static/uploads")
upload_dir.mkdir(parents=True, exist_ok=True)

with open(upload_dir / "dummy_logo.png", "wb") as f:
    f.write(b"dummy_logo_content")
with open(upload_dir / "dummy_photo.png", "wb") as f:
    f.write(b"dummy_photo_content")
with open(upload_dir / "dummy_reference.pdf", "wb") as f:
    f.write(b"dummy_reference_content")