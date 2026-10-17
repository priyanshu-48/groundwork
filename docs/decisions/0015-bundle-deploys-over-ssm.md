# 0015: Deploy by S3 bundle and SSM Run Command (no SSH, no registry, no keys)
- **Context:** the owner runs every AWS command (Claude never does) and no access keys may exist anywhere. SPEC suggests ECR plus an SSH deploy from GitHub Actions.
- **Decision:** a tarball of the repo goes to a private S3 bucket from AWS CloudShell (already signed in), and AWS Systems Manager Run Command tells the instance to unpack it, refresh secrets from Parameter Store, `docker compose up -d --build`, and wait for `/health`. The previous release stays on disk for `--rollback`. Port 22 is closed; shell access is Session Manager.
- **Why:** no credentials leave AWS, no keys to rotate or leak, no registry cost; the same `release.sh` works on any host with the bundle copied over (Oracle: `scp`).
- **Trade-offs:** building on the instance is slower than pulling images (5-10 minutes first time); not automated from GitHub (a push does not deploy). An OIDC role for GitHub Actions can be added later if wanted.
- **Safety:** SSM commands and their output never contain secret values (`fetch-env.sh` prints only a line count).
