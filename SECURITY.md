# Security policy

## Reporting a problem

If you find a security issue, **do not open a public issue**. Use GitHub's private "Report a vulnerability" option on the Security tab of this repository, or contact the maintainer through the email on their GitHub profile.

Please include what you found, how to reproduce it, and which version you used. You can expect a first reply within about a week.

## Things to know when using this project

- RTSP URLs usually contain a camera password. Keep them in `config.yaml` (git-ignored) and never commit them.
- Model files are downloaded by `scripts/download_models.py` and checked against a pinned SHA-256 hash.
- Video of people can be personal data. Follow the laws and consent rules that apply where you run it.
