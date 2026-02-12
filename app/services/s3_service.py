import boto3
import os
import uuid

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def upload_file_to_s3(file_bytes: bytes, filename: str, folder: str, content_type: str):
    key = f"{folder}/{uuid.uuid4()}-{filename}"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
        # ACL="public-read"   # IMPORTANT
    )
    url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
    return url

def get_s3_key_from_url(file_url: str) -> str | None:
    if not file_url:
        return None
    if "amazonaws.com/" not in file_url:
        return None
    return file_url.split(".amazonaws.com/")[-1]


def delete_file_from_s3(file_url: str):
    key = get_s3_key_from_url(file_url)
    if not key:
        return
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)
        print(f"S3 deleted: {key}")
    except Exception as e:
        print(f"[S3 Delete Error]: {e}")

