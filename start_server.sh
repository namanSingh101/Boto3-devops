#! /bin/bash

set -eou pipefail

EC2_ip=$1
PLATFORM=ubuntu
FILE=~/Downloads/key_mumbai_region.pem

chmod 400 $FILE

ssh-add $FILE
ssh -i $FILE -A $PLATFORM@$EC2_ip

