import boto3
import json
from botocore.exceptions import ClientError

#define bucket name and region
bucket_name = "bucket_name(unique)"
region = "region"

session = boto3.Session(profile_name="aws_cli_profile")
s3_client = session.client("s3",region_name=region)
sts = session.client('sts')

identity = sts.get_caller_identity()
iam_user_arn = identity['Arn']
print(f"👤 Bucket will be created by IAM entity: {iam_user_arn}")

#create s3 bucket
def create_s3_bucket(bucket_name,region):
    try:
        response = s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint':region}
        )
        print(f"Bucket {bucket_name} created successfully in {region}")
    except ClientError as e:
        if "BucketAlreadyOwnedByYou" in str(e):
            print(f"Bucket {bucket_name} already exists")
        else:
            raise e
        
def block_public_access():
    try:
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
               'BlockPublicPolicy': True,
               'RestrictPublicBuckets': True
                }
        )
        print("Public access sucessfuly blocked for the bucket")
    except ClientError as e:
        print(f"Failed to set public access block {e}")

def attach_bucket_policy():
    try:
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowReadAccessToSpecificUser",
                    "Effect": "Allow",
                    "Principal": {"AWS": iam_user_arn},
                    "Action": ["s3:GetObject"],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }

        policy_json = json.dumps(bucket_policy)

        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=policy_json)
        print("📜 Bucket policy applied successfully. Access restricted to IAM user only.")

    except ClientError as e:
        print(f"❌ Error setting bucket policy: {e}")


if __name__ == "__main__":
    create_s3_bucket(bucket_name,region)
    block_public_access()
    attach_bucket_policy()