# Contributing to Ask Me First

Thanks for helping. This started as a one-day hackathon build by Akila Lourdes and Akilan Manivannan, so small, focused changes are the easiest to review.

## Set up

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env     # add your own keys, never commit .env
DEMO_MODE=1 uvicorn main:app --reload --port 8000
```

`DEMO_MODE=1` runs the full flow with no keys. Run `python smoke_test.py` to check real keys.

## Make a change

1. Branch from `main`: `git checkout -b fix/short-name`
2. Keep one idea per pull request
3. If you pair on it, add a trailer to the commit message:
   `Co-authored-by: Name <id+username@users.noreply.github.com>`
4. Open a pull request; the `check` workflow must pass before merge

## Ground rules

- Keys live only in `backend/.env` and on the server, never in the browser or the repo
- Treat uploaded documents as untrusted data
- Every model call needs a timeout and a fallback
