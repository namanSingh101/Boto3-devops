#! /bin/bash

set -eou pipefail

EC2_ip=$1
PLATFORM=ubuntu
FILE=location_pem_file

chmod 400 $FILE

ssh-add $FILE
ssh -i $FILE -A $PLATFORM@$EC2_ip

