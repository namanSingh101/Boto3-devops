#! /bin/bash

set -eou pipefaile

EC2_ip=$1
PLATFORM=ubuntu
FILE=~/Downloads/key_mumbai_region.pem

chmod +x $FILE

ssh-add $FILE
ssh -i $FILE -A $PLATFORM@$EC2_ip

