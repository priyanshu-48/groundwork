# Moving from AWS to Oracle Cloud (free tier)

Written during M9, while the design is fresh. The AWS free plan ends **2027-04-17**. The deployment was
shaped (ADR 0014) so this move needs configuration and a new host, **not application code changes**.

## What stays exactly the same
`docker-compose.prod.yml`, the Caddyfile, all images (built on the host from the same bundle), the
Postgres container, every line of app code, `smoke.py`, `backup.sh`, `restore.sh`, `release.sh`.

## What changes (checklist)
| # | Area | AWS today | Oracle |
|---|---|---|---|
| 1 | Host | EC2 t4g.small, Ubuntu 24.04 arm64 | Ampere A1 VM (arm64) with Ubuntu 24.04: same images, same `instance-setup.sh` as cloud-init or run by hand |
| 2 | Object storage | S3 via instance role (no keys) | Object Storage S3-compatible endpoint: set `S3_ENDPOINT_URL=https://<namespace>.compat.objectstorage.<region>.oraclecloud.com`, `S3_REGION=<region>`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` (a "customer secret key" you create in the Oracle console; the only place a key exists) |
| 3 | Secrets | SSM Parameter Store via `fetch-env.sh` | replace `fetch-env.sh` only: write `/opt/groundwork/runtime.env` from Oracle Vault, or by hand with mode 600 |
| 4 | Network | security group 80/443 | VCN security list + the VM's iptables rules for 80/443 (Oracle Ubuntu images ship restrictive iptables) |
| 5 | Hostname | `<ip-dashed>.sslip.io` | the same pattern works with the VM's public IP; or a real domain with an A record |
| 6 | Deploy | S3 bundle + SSM Run Command | upload the same bundle (`scp`, or Object Storage) and run `release.sh <bundle>`; a small `deploy/oracle/` folder would hold this |
| 7 | Data | EBS volume + nightly dump | restore the latest dump with `restore.sh`, copy bucket contents (`aws s3 sync` works against both endpoints) |
| 8 | `host.env` | `AWS_REGION`, `S3_BUCKET`, `SITE_HOST` | same file, add `S3_ENDPOINT_URL` (the scripts already honour it) |

## Order of operations
1. Create the VM and bucket; run `instance-setup.sh`; write `runtime.env` with the Oracle S3 settings.
2. Deploy the bundle with `release.sh`; run `smoke.py` against the new IP.
3. On AWS: `backup.sh`, then `aws s3 sync` the bucket to Oracle; on Oracle: `restore.sh <key>`.
4. Point users at the new hostname; keep AWS stopped (not deleted) for a week; then `99-teardown.sh`.

## AWS-specific vs portable
AWS-specific (isolated in `deploy/aws/`): bucket/role/security-group/instance creation, SSM parameters,
Run Command, Elastic IP. Everything else, including `deploy/common/`, runs on any Docker host.
