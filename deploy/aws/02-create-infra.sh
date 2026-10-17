#!/usr/bin/env bash
# Creates the AWS resources: private S3 bucket, IAM role (least privilege), firewall (80/443 only),
# one EC2 instance and an Elastic IP. Every resource id is written to deploy/aws/state.env as it is
# created, so 99-teardown.sh can remove exactly these and nothing else. Safe to re-run: existing
# resources are skipped.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready

BUCKET="$NAME-$ACCOUNT_ID-$REGION"
ROLE="$NAME-ec2"

cat <<EOF
About to create in account $ACCOUNT_ID, region $REGION:
  - S3 bucket        $BUCKET   (private, encrypted, TLS-only, lifecycle: bundles 30 d, backups 14 d)
  - IAM role         $ROLE     (read /$NAME/* parameters, use only that bucket, SSM session access)
  - Security group   $NAME-sg  (inbound 80 and 443 only; NO ssh)
  - EC2 instance     $INSTANCE_TYPE Ubuntu 24.04 arm64, ${DISK_GB} GB encrypted gp3, IMDSv2 required
  - Elastic IP       attached to the instance
Estimated cost ~ \$19/month from credits while running (see 01-preflight.sh). Nothing else is touched.
EOF
confirm "Create these resources?" || die "aborted, nothing created"

tags="ResourceType=%s,Tags=[{Key=Project,Value=$NAME},{Key=Name,Value=$NAME}]"

# ---- S3 bucket
if aws_ s3api head-bucket --bucket "$BUCKET" 2>/dev/null; then
  echo "bucket exists: $BUCKET"
else
  aws_ s3api create-bucket --bucket "$BUCKET" \
    --create-bucket-configuration "LocationConstraint=$REGION" >/dev/null
fi
state_set BUCKET "$BUCKET"
aws_ s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws_ s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
aws_ s3api put-bucket-policy --bucket "$BUCKET" --policy "$(cat <<EOF
{"Version":"2012-10-17","Statement":[{"Sid":"TlsOnly","Effect":"Deny","Principal":"*","Action":"s3:*",
"Resource":["arn:aws:s3:::$BUCKET","arn:aws:s3:::$BUCKET/*"],
"Condition":{"Bool":{"aws:SecureTransport":"false"}}}]}
EOF
)"
aws_ s3api put-bucket-lifecycle-configuration --bucket "$BUCKET" --lifecycle-configuration '{"Rules":[
{"ID":"expire-bundles","Status":"Enabled","Filter":{"Prefix":"bundles/"},"Expiration":{"Days":30}},
{"ID":"expire-backups","Status":"Enabled","Filter":{"Prefix":"backups/"},"Expiration":{"Days":14}},
{"ID":"abort-partial-uploads","Status":"Enabled","Filter":{"Prefix":""},"AbortIncompleteMultipartUpload":{"DaysAfterInitiation":3}}]}'
echo "bucket ready"

# ---- IAM role and instance profile
if ! aws_ iam get-role --role-name "$ROLE" >/dev/null 2>&1; then
  aws_ iam create-role --role-name "$ROLE" --tags "Key=Project,Value=$NAME" --assume-role-policy-document \
    '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null
fi
state_set ROLE "$ROLE"
aws_ iam attach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws_ iam put-role-policy --role-name "$ROLE" --policy-name "$NAME-app" --policy-document "$(cat <<EOF
{"Version":"2012-10-17","Statement":[
{"Sid":"ReadOwnParameters","Effect":"Allow","Action":["ssm:GetParametersByPath","ssm:GetParameters","ssm:GetParameter"],
 "Resource":"arn:aws:ssm:$REGION:$ACCOUNT_ID:parameter/$NAME*"},
{"Sid":"ListOwnBucket","Effect":"Allow","Action":["s3:ListBucket","s3:GetBucketLocation"],"Resource":"arn:aws:s3:::$BUCKET"},
{"Sid":"ObjectsInOwnBucket","Effect":"Allow","Action":["s3:GetObject","s3:PutObject","s3:DeleteObject"],"Resource":"arn:aws:s3:::$BUCKET/*"}]}
EOF
)"
if ! aws_ iam get-instance-profile --instance-profile-name "$ROLE" >/dev/null 2>&1; then
  aws_ iam create-instance-profile --instance-profile-name "$ROLE" >/dev/null
  aws_ iam add-role-to-instance-profile --instance-profile-name "$ROLE" --role-name "$ROLE"
  echo "waiting for the instance profile to propagate..."
  sleep 15
fi
state_set INSTANCE_PROFILE "$ROLE"

# ---- security group (default VPC)
VPC="$(aws_ ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)"
[ "$VPC" != None ] || die "no default VPC in $REGION"
SG="$(state_get SECURITY_GROUP)"
if [ -z "$SG" ]; then
  SG="$(aws_ ec2 create-security-group --group-name "$NAME-sg" --description "Groundwork web 80/443 only" \
    --vpc-id "$VPC" --tag-specifications "$(printf "$tags" security-group)" --query GroupId --output text)"
  state_set SECURITY_GROUP "$SG"
  aws_ ec2 authorize-security-group-ingress --group-id "$SG" --ip-permissions \
    'IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0}],Ipv6Ranges=[{CidrIpv6=::/0}]' \
    'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0}],Ipv6Ranges=[{CidrIpv6=::/0}]' >/dev/null
fi
echo "security group: $SG"

# ---- instance
IID="$(state_get INSTANCE_ID)"
if [ -z "$IID" ]; then
  AMI="$(aws_ ssm get-parameter --name /aws/service/canonical/ubuntu/server/24.04/stable/current/arm64/hvm/ebs-gp3/ami-id \
    --query Parameter.Value --output text)"
  IID="$(aws_ ec2 run-instances --image-id "$AMI" --instance-type "$INSTANCE_TYPE" --count 1 \
    --iam-instance-profile "Name=$ROLE" --security-group-ids "$SG" \
    --metadata-options 'HttpTokens=required,HttpPutResponseHopLimit=2,HttpEndpoint=enabled' \
    --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=$DISK_GB,VolumeType=gp3,Encrypted=true,DeleteOnTermination=true}" \
    --user-data "file://$REPO_ROOT/deploy/common/instance-setup.sh" \
    --tag-specifications "$(printf "$tags" instance)" "$(printf "$tags" volume)" \
    --query 'Instances[0].InstanceId' --output text)"
  state_set INSTANCE_ID "$IID"
fi
# HttpPutResponseHopLimit=2 lets containers (one network hop further) reach the instance role.
echo "instance: $IID (waiting until running)"
aws_ ec2 wait instance-running --instance-ids "$IID"

# ---- Elastic IP
ALLOC="$(state_get ALLOCATION_ID)"
if [ -z "$ALLOC" ]; then
  ALLOC="$(aws_ ec2 allocate-address --domain vpc --tag-specifications "$(printf "$tags" elastic-ip)" \
    --query AllocationId --output text)"
  state_set ALLOCATION_ID "$ALLOC"
fi
aws_ ec2 associate-address --instance-id "$IID" --allocation-id "$ALLOC" >/dev/null
IP="$(aws_ ec2 describe-addresses --allocation-ids "$ALLOC" --query 'Addresses[0].PublicIp' --output text)"
HOST="${IP//./-}.sslip.io"
state_set PUBLIC_IP "$IP"
state_set SITE_HOST "$HOST"

echo "waiting for the instance to register with Systems Manager (up to 5 minutes)..."
for _ in $(seq 30); do
  online="$(aws_ ssm describe-instance-information --filters "Key=InstanceIds,Values=$IID" \
    --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null || true)"
  [ "$online" = Online ] && break
  sleep 10
done
[ "$online" = Online ] || echo "NOTE: not online yet; wait a minute and re-run 04-deploy.sh (it waits as well)."

cat <<EOF

Done. Address: https://$HOST  (comes alive after 04-deploy.sh)
Resources are listed in $STATE_FILE
Next: 03-set-secrets.sh, then 04-deploy.sh
EOF
