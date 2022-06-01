#!/usr/bin/env python3

from twitter_stream import TwitterStream
from dotenv import load_dotenv
from minio import Minio
import os

load_dotenv()

s3_bucket = os.environ.get("S3_BUCKET")
s3_prefix = os.environ.get("S3_PREFIX")
s3_url = os.environ.get("S3_URL")
s3_access_key = os.environ.get("S3_ACCESS_KEY")
s3_secret_key = os.environ.get("S3_SECRET_KEY")
bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")

def main():
    s3_client = Minio(s3_url, access_key=s3_access_key, secret_key=s3_secret_key)
    stream = TwitterStream(s3_client=s3_client, bucket=s3_bucket, twitter_bearer_token=bearer_token, prefix=s3_prefix)
    stream.run()

if __name__ == '__main__':
    main()

