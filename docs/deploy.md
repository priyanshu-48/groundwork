# Deploying Groundwork to AWS (CloudShell runbook)

Everything below runs in **AWS CloudShell** (console, top bar, terminal icon), which is already signed in
as you. No access keys, nothing installed on your laptop. Claude wrote these scripts; you run them.
Each one prints what it will create and asks you to type `yes`. Region is fixed to `ap-southeast-2`
(Sydney) inside the scripts. Architecture and costs: `docs/architecture.md`, ADR 0014/0015.

## One-time checks (console)
Zero-spend budget exists, Google account has 2-step verification, you are on the Free plan. Do **not**
click Upgrade.

## 1. Get the code into CloudShell
On your laptop, after the commit you want to deploy:

```bash
git archive --format=tar.gz -o groundwork.tgz HEAD
```

In CloudShell: delete any older archive first (`rm -f ~/groundwork.tgz`, CloudShell never overwrites an upload), then **Actions → Upload file** → `groundwork.tgz`, then:

```bash
mkdir -p ~/groundwork && tar -xzf groundwork.tgz -C ~/groundwork && cd ~/groundwork
```

(Re-deploys: upload a new archive and extract over the same folder; `deploy/aws/state.env` is not in the
archive, so it survives.)

## 2. Create, configure, deploy
```bash
bash deploy/aws/01-preflight.sh        # read-only: account, budget, allowed instance types, cost
bash deploy/aws/02-create-infra.sh     # bucket, role, firewall, instance, Elastic IP (asks yes)
bash deploy/aws/03-set-secrets.sh      # hidden prompt for the Gemini key; prints the invite code
bash deploy/aws/04-deploy.sh           # build on the instance, start, wait until healthy (5-10 min)
```

If preflight says `t4g.small` is not allowed on your plan, re-run with a smaller type from its list:
`INSTANCE_TYPE=t4g.micro bash deploy/aws/02-create-infra.sh` (1 GB RAM is tight; swap is configured).

## 3. Check it works
```bash
python3 deploy/common/smoke.py "https://$(grep SITE_HOST deploy/aws/state.env | cut -d= -f2)" \
  --code "$(bash deploy/aws/show-secret.sh SIGNUP_CODE)" \
  --admin-token "$(bash deploy/aws/show-secret.sh ADMIN_TOKEN)"
```
Expect `ALL PASSED`. It creates a throwaway workspace and uses a handful of free-tier Gemini calls.
Open the URL in a browser too (the first request waits a few seconds for the HTTPS certificate).

## Day to day
| Task | Command |
|---|---|
| Deploy a new version | upload a new archive (step 1), `bash deploy/aws/04-deploy.sh` |
| Roll back | `bash deploy/aws/04-deploy.sh --rollback` |
| Pause (no compute charge) | `bash deploy/aws/stop.sh` / `bash deploy/aws/start.sh` |
| Look at logs | Console → EC2 → instance → **Connect → Session Manager**, then `cd /opt/groundwork/current && sudo docker compose --env-file /opt/groundwork/runtime.env -f docker-compose.prod.yml logs --tail 100 api` |
| Metrics | `curl -H "X-Admin-Token: $(bash deploy/aws/show-secret.sh ADMIN_TOKEN)" https://<host>/api/admin/metrics` |
| Backup now | in the Session Manager shell: `sudo /opt/groundwork/current/deploy/common/backup.sh` (also nightly 03:15 UTC) |
| Restore | `sudo /opt/groundwork/current/deploy/common/restore.sh latest` (asks first) |
| Delete everything | `bash deploy/aws/99-teardown.sh` (asks before each group) |

Every log line is JSON with a `request_id`; the browser shows it as the `X-Request-ID` response header.

## Restore drill (do it once)
1. Run a backup, note the key it prints.
2. Upload a document in the UI, then restore the backup taken **before** it.
3. The document is gone and the app still works. Restoring replaces database contents; uploaded PDFs
   stay in the bucket (they are only re-linked by the database).

## Local dry run (no AWS)
Rehearses the production compose file with a throwaway S3 and the fake provider:

```bash
printf 'POSTGRES_PASSWORD=dry\nJWT_SECRET=%s\nS3_BUCKET=groundwork-dry\nSITE_HOST=http://localhost\nAI_PROVIDER=fake\nADMIN_TOKEN=dry-admin\nSIGNUP_CODE=dry-code\n' "$(openssl rand -hex 32)" > /tmp/dry.env
docker compose -p gwdry --env-file /tmp/dry.env -f docker-compose.prod.yml -f deploy/common/compose.dryrun.yml up -d --build
python deploy/common/smoke.py http://localhost --code dry-code --admin-token dry-admin
docker compose -p gwdry --env-file /tmp/dry.env -f docker-compose.prod.yml -f deploy/common/compose.dryrun.yml down -v
```

## Safety notes
- Secrets live only in SSM Parameter Store and in `/opt/groundwork/runtime.env` (mode 600) on the instance.
  They are never in git, the bundle, logs, or this chat. `state.env` holds resource ids only.
- Only ports 80/443 are open. There is no SSH; shell access is Session Manager.
- Public signups are closed by the invite code. Only synthetic documents on the free Gemini tier.
- CloudShell storage is per region and can be deleted after long inactivity. Resource ids are also listed
  in `docs/journal.md`, so teardown is possible without `state.env`.
