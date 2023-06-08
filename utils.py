import os
from dotenv import load_dotenv

import boto3
from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ['AWS_REGION']
AWS_BUCKET_NAME = os.environ['AWS_BUCKET_NAME']


def upload_image(file, username):
    s3 = boto3.client(
        "s3",
        AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    aws_filename = f"{username}-{file.filename}"

    s3.upload_fileobj(file, AWS_BUCKET_NAME, aws_filename)

    return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{aws_filename}"
