# Link-Up Docs

Official documentation for Link-Up Odoo packages.

**Live site:** [docs.link-up.co.kr](https://docs.link-up.co.kr)

## Local Development

```bash
# Install dependencies
pip install -r docs/requirements.txt

# Build HTML
make html

# Live preview (auto-reload)
pip install sphinx-autobuild
make livehtml
```

## Deployment

Documentation is automatically built and deployed to GitHub Pages via GitHub Actions on every push to `main`.

## Structure

```
docs/
├── ai-agent/        # AI Agent modules
├── localization/     # Korean localization
├── messaging/        # KakaoTalk, SMS
├── commerce/         # Coupang, Naver, delivery
├── marketing/        # Email/SMS campaigns
└── integrations/     # PG payments, APIs
```
