# Security policy

## Report a problem privately

Found a leaked key, a way to reach the API keys, or a bug that exposes someone's writing?
Please **do not open a public issue**. Use **Security → Report a vulnerability** on this repository instead.
Only the maintainers can see those reports.

We aim to reply within 7 days.

## What counts

| In scope | Examples |
|---|---|
| 🔑 Secrets | A key in the repo, the browser, logs or an error message |
| 📄 Uploads | A file type or size that gets past the upload limits, or temp files that are not deleted |
| 💬 Prompt injection | An uploaded document that makes the app ignore its rules or leak data |
| 🚦 Abuse | A way around the rate limit that burns the API budget |

## How the app protects keys

- Keys live only in `backend/.env` or the host's secret store, never in the page
- `.env` is git-ignored and Docker-ignored, and CI fails if a real key lands in `.env.example`
- Uploaded documents are treated as untrusted data, never as instructions
- POST endpoints are rate limited per visitor; errors never show internal details

## If you committed a key by mistake

1. Revoke it at the provider **first**. Deleting the commit is not enough, because it stays in history and forks.
2. Create a new key and put it only in `backend/.env`.
3. Tell the maintainers so the history can be cleaned.
