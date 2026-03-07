from strands import tool
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

@tool
def list_buckets():
    """List all available S3 buckets"""
    response = s3.list_buckets()
    return [b["Name"] for b in response["Buckets"]]


@tool
def browse_bucket(bucket: str, prefix: str = ""):
    """Browse files inside an S3 bucket"""
    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix,
        MaxKeys=50
    )

    return [obj["Key"] for obj in response.get("Contents", [])]


@tool
def search_files(bucket: str, query: str):
    """Search for files containing a string"""
    response = s3.list_objects_v2(Bucket=bucket)

    matches = []
    for obj in response.get("Contents", []):
        if query.lower() in obj["Key"].lower():
            matches.append(obj["Key"])

    return matches


@tool
def read_file(bucket: str, key: str):
    """Read a text file from S3"""
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8")


@tool
def upload_file(bucket: str, local_path: str, key: str):
    """Upload file to S3"""
    s3.upload_file(local_path, bucket, key)
    return f"Uploaded {local_path} to {bucket}/{key}"


@tool
def generate_download_url(bucket: str, key: str):
    """Generate temporary download URL"""
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=3600
    )