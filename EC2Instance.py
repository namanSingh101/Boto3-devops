import boto3
import json
from botocore.exceptions import ClientError
import sys
import subprocess
import socket
import time

region="region"
profile="profile"
ami_id="ami-0f918f7e67a3323f0"     #ubuntu ami 
key_name="key_pair"
subnet_id="subnet_id"
sg_id="security_group"
bash_script="./start_server.sh"

session=boto3.Session(profile_name=profile,region_name=region)
sts = session.client("sts")
ec2 = session.resource("ec2")

identity=sts.get_caller_identity()
iam_user_arn = identity['Arn']
print(f"Bucket will be created by IAM entity: {iam_user_arn}")

def create_instance(subnet_id,sg_id,ami_id):
    try:
        print("Launching ec2 instance ...")
        instances=ec2.create_instances(
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
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xya1', #change it 
                 'Ebs': {
                    'VolumeSize': 15,   # 15 GB
                    'VolumeType': 'gp3',
                    'DeleteOnTermination': True
                }
            }
        ],
    TagSpecifications=[{
        "ResourceType": "instance",
        "Tags": [{"Key": "Name", "Value": "boto3-jenkins-instance"}]
    }]
        )
        instance=instances[0]
        instance_id=instance.id
        print(f"EC2 Instance {instance_id} created . Waitng for running the EC2")

        instance.wait_until_running()
        instance.reload()

        print(f"EC2 Instance IP address {instance.public_ip_address} created")
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
    
def wait_for_ssh(ip, port=22, timeout=300):
    print("Waiting for SSH to become available...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((ip, port))
            sock.close()
            print("✅ SSH is now reachable!")
            return True
        except Exception:
            print(".", end="", flush=True)
            time.sleep(5)
    raise TimeoutError("SSH not reachable within timeout period")


if __name__=="__main__":
    public_ip=create_instance(subnet_id,sg_id,ami_id)
    wait_for_ssh(public_ip)
    shell_script(public_ip)
