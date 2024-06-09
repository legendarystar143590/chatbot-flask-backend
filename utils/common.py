import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_ACCESS_KEY_ID = os.getenv("BUCKET_ACCESS_KEY_ID")
BUCKET_SECRET_ACCESS_KEY = os.getenv("BUCKET_SECRET_ACCESS_KEY")
BUCKET_ENDPOINT = os.getenv("BUCKET_ENDPOINT")

# Configure the DigitalOcean Spaces client
session = boto3.session.Session()
client = session.client('s3',
                        region_name='aiana',
                        endpoint_url=BUCKET_ENDPOINT,
                        aws_access_key_id=BUCKET_ACCESS_KEY_ID,
                        aws_secret_access_key=BUCKET_SECRET_ACCESS_KEY)

# Function to get the bucket name of a DigitalOcean Space
def get_bucket_name():
    try:
        response = client.list_buckets()
        print(response)
    except Exception as e:
        print(f"Error: {str(e)}")

# Upload image to DigitalOcean Spaces
def upload_image_to_spaces(image_path, bucket_name, object_name):
    try:
        client.upload_file(image_path, bucket_name, object_name)
        print(f"Image uploaded successfully to DigitalOcean Spaces.", url)
        image_url = f"https://{bucket_name}.ams3.digitaloceanspaces.com/{object_name}"
        return image_url
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return None

def get_language_code(language_name):
    # Dictionary mapping full language names to ISO 639-1 codes
    languages = {
        'English': 'en',
        'French': 'fr',
        'Spanish': 'es',
        'German': 'de',
        'Chinese': 'zh',
        'Dutch':'nl',
        # Add more languages as needed
    }

    # Return the language code, defaulting to 'en' if not found
    return languages.get(language_name, 'en')

def get_language_name(language_code):
    # Dictionary mapping ISO 639-1 codes to full language names
    codes_to_languages = {
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'zh': 'Chinese',
        'nl': 'Dutch',
        # Add more mappings as needed
    }

    # Return the full language name, defaulting to 'English' if the code is not found
    return codes_to_languages.get(language_code, 'English')

def get_url_from_name(name):
    imageUrl = client.generate_presigned_url(
        ClientMethod = 'get_object',
        Params={
            'Bucket':'aiana',
            'Key':name
        },
        ExpiresIn=60
    )
    return imageUrl