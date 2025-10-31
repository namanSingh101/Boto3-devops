import boto3
import json
from botocore.exceptions import ClientError
import sys
import subprocess

region="ap-south-1"
profile="terraform"
ami_id="ami-0f918f7e67a3323f0"
key_name="key_mumbai_region"
subnet_id="subnet-0371715cc6e1eaed7"
sg_id="sg-05a15917a59257cc2"
bash_script="./start_server.sh"

session=boto3.Session(profile_name=profile)
sts=session.client("sts")
ec2=session.client("ec2")

identity=sts.get_caller_identity()
iam_user_arn = identity['Arn']
print(f"Bucket will be created by IAM entity: {iam_user_arn}")

def create_instance(profile_name,subnet_id,sg_id,ami_id):
    try:
        print("Launching ec2 instance ...")
        instances=ec2.create_instance(
            ImageId=ami_id,
        InstanceType="t2.micro",
        KeyName=key_name,
        MinCount=1,
        MaxCount=1,
        NetworkInterfaces=[{
        "SubnetId": subnet_id,
        "DeviceIndex": 0,
        "AssociatePublicIpAddress": True,
        "Groups": [sg_id]
    }],
    TagSpecifications=[{
        "ResourceType": "instance",
        "Tags": [{"Key": "Name", "Value": "boto3-jenkins-instance"}]
    }]
        )
        instance=instance[0]
        instance_id=instances[0].id
        print(f"EC2 Instance {instance_id} created . Waitng for running the EC2")

        instance.wait_until_running()
        instance.reload()


        return instance.public_ip_address
    except ClientError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

def shell_script(public_ip):
    try:
        subprocess.run(["bash", bash_script, public_ip], check=True)
        print("Automation Complete...")
    except Exception as e:
        raise e
    

if __name__=="__main__":
    public_ip=create_instance(profile,subnet_id,sg_id,ami_id)
    shell_script(public_ip)