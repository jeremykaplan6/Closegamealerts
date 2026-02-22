# Run Close Game Detector Without Your Laptop

The script supports **one-shot mode** so a cloud scheduler can run it every few minutes. No need for your laptop or an always-on server.

## One-shot mode

```bash
python3 day06_close_game_detector.py --once
# or
python3 day06_close_game_detector.py -o
```

- Runs a single check and exits.
- Saves "already alerted" state to `.close_game_alerted.json` in the same folder so the next run won’t send duplicate alerts.

## Option 1: GitHub Actions (free, no server)

1. Push this repo to GitHub.
2. Add your Pushover keys as **repository secrets**: `PUSHOVER_APP_TOKEN`, `PUSHOVER_USER_KEY`.
3. Create `.github/workflows/close-game.yml` (see below).
4. The workflow runs every 5 minutes and executes the script in one-shot mode.

**Limitation:** GitHub Actions has a free-tier limit (e.g. 2000 min/month); 5-min cron uses ~8640 min/month, so you may need a paid plan or a less frequent schedule (e.g. every 15 min).

## Option 2: Cheap VPS (~$5/month or free tier)

- **DigitalOcean**, **Linode**, **Oracle Cloud** (free tier), **AWS** (free tier 12 months), etc.
- On the server: install Python 3 + `requests`, clone or copy your script (and state file if you want to preserve alerts).
- Run in a loop with `nohup` or systemd, or run one-shot every 5 minutes via cron:

  ```bash
  */5 * * * * cd /path/to/ai-gym && /usr/bin/python3 day06_close_game_detector.py --once >> /var/log/close_game.log 2>&1
  ```

## Option 3: Serverless / cron (e.g. AWS Lambda, Google Cloud Scheduler)

- Package the script and dependencies (e.g. Lambda layer or zip with `requests`).
- Set up a scheduled trigger (e.g. every 5 minutes).
- Invoke the script in one-shot mode. Persist `.close_game_alerted.json` in S3 or similar so state is shared between invocations.

## Summary

| Method              | Cost        | Effort | Best for                    |
|---------------------|------------|--------|-----------------------------|
| GitHub Actions cron | Free / paid| Low    | Try it first                |
| VPS + cron or loop  | ~$5/mo     | Medium | Reliable, full control      |
| Lambda + S3 state   | Very low   | Higher | Scale-to-zero, more setup    |

Use **`--once`** for any scheduled or serverless run so each invocation is a single check and state is loaded/saved from disk.
