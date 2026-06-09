import requests
import json
from pathlib import Path

# Base URL of your Flask application
# Make sure your Flask app is running when you execute this script
BASE_URL = "http://127.0.0.1:5000" 
SUBMIT_URL = f"{BASE_URL}/api/onboard/submit"

# --- 1. Prepare Form Data ---
# These fields should match the form fields expected by your /api/onboard/submit endpoint
# Ensure all 'required' fields from app.py are included.
form_data = {
    "company_name": "Test Company Inc.",
    "contact_name": "Test User",
    "contact_email": "test@example.com",
    "main_goal": "To test the n8n integration",
    "terms": "on",  # Represents the checkbox being checked
    "industry": "Software",
    "job_title": "Developer",
    "phone": "123-456-7890",
    "address": "123 Test Street",
    "existing_url": "https://www.testcompany.com",
    "referral_source": "Google",
    "services": "Web Development,SEO",
    "target_audience": "Small Businesses",
    "competitors": "Competitor A, Competitor B",
    "likes_competitors": "Clean UI",
    "dislikes_competitors": "Slow performance",
    "has_content": "yes",
    "page_count": "10",
    "pages_needed": "About Us,Contact,Services",
    "needs_blog": "yes",
    "sells_online": "no",
    "product_count": "",
    "languages": "English",
    "multilingual": "no",
    "seo_history": "some",
    "paid_ads": "no",
    "target_keywords": "testing,integration",
    "google_business": "yes",
    "analytics_setup": "yes",
    "social_platforms": "LinkedIn,Twitter",
    "launch_date": "2024-12-31",
    "deadline_urgency": "high",
    "budget": "$10000 - $20000",
    "payment_preference": "Bank Transfer",
    "maintenance_budget": "$500 - $1000",
    "involvement_level": "medium",
    "main_contact_name": "Test User",
    "main_contact_email": "test@example.com",
    "integrations": "CRM,Payment Gateway",
    "other_notes": "This is a test submission from test.py script.",
    "digital_presence_rating": "4",
    "primary_colour": "#FF0000",
    "secondary_colour": "#0000FF",
    "font_preferences": "Roboto,Arial",
}

# --- 2. Prepare Files for Upload ---
# Paths to the dummy files created earlier
upload_dir = Path("static/uploads")
logo_path = upload_dir / "dummy_logo.png"
photo_path = upload_dir / "dummy_photo.png"
reference_path = upload_dir / "dummy_reference.pdf"

# Open files in binary read mode
files_to_upload = {
    "logo": (logo_path.name, open(logo_path, "rb"), "image/png"),
    "brand_photos": (photo_path.name, open(photo_path, "rb"), "image/png"),
    "reference_files": (reference_path.name, open(reference_path, "rb"), "application/pdf"),
}

# --- 3. Send the POST Request ---
print(f"Sending POST request to {SUBMIT_URL}...")
try:
    response = requests.post(SUBMIT_URL, data=form_data, files=files_to_upload)

    # --- 4. Process the Response ---
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
    except json.JSONDecodeError:
        print(f"Response Text: {response.text}")

    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    print("\nSuccessfully submitted form data and files.")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except requests.exceptions.ConnectionError as conn_err:
    print(f"Connection error occurred: {conn_err}. Is the Flask app running at {BASE_URL}?")
except requests.exceptions.Timeout as timeout_err:
    print(f"Timeout error occurred: {timeout_err}")
except requests.exceptions.RequestException as req_err:
    print(f"An unexpected error occurred: {req_err}")
finally:
    # Ensure all opened files are closed
    for file_field, file_info in files_to_upload.items():
        if isinstance(file_info, list): # Handle multiple files for a field
            for f_name, f_obj, f_type in file_info:
                f_obj.close()
        else: # Handle single file for a field
            f_name, f_obj, f_type = file_info
            f_obj.close()
    print("\nFiles closed.")
