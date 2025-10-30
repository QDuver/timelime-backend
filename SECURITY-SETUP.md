# Security Setup Guide

This document outlines the security measures implemented in this repository and provides setup instructions.

## Environment Variables

This application uses environment variables to store sensitive information. **Never commit API keys, passwords, or credentials directly in the code.**

### Required Environment Variables

All required environment variables are documented in `.env.example`. Copy this file to create your local `.env` file:

```bash
cp .env.example .env
```

Then fill in your actual values.

### For Local Development

1. Create a `.env` file based on `.env.example`
2. Set all required environment variables
3. For GCP credentials, you can either:
   - Set `GCP_CREDENTIALS` to the JSON credentials string
   - Or use `LOCAL_DEV_CREDENTIALS_PATH` to point to a local JSON file

### For Production/Pre-production Deployment

Set the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

**Pre-production:**
- `GCP_CREDENTIALS_PREPROD`
- `OPENAI_API_KEY_PREPROD`
- `STRIPE_PREPROD`
- `STRIPE_WEBHOOK_PREPROD`
- `SENDGRID_API_KEY_PREPROD`
- `CONTACT_EMAIL`
- `ADMIN_EMAIL`

**Production:**
- `GCP_CREDENTIALS_PROD`
- `OPENAI_API_KEY_PROD`
- `STRIPE_PROD`
- `STRIPE_WEBHOOK_PROD`
- `SENDGRID_API_KEY_PROD`
- `CONTACT_EMAIL`
- `ADMIN_EMAIL`

## Important Security Notes

### Before Making This Repository Public

1. **Revoke any previously committed API keys** - If this repository was ever public or keys were committed in git history, those keys must be revoked and regenerated:
   - Generate new SendGrid API key
   - Rotate any other credentials that may have been exposed

2. **Check Git History** - Use tools like `git-secrets` or `truffleHog` to scan git history for accidentally committed secrets

3. **Set Up GitHub Secrets** - Ensure all required secrets are configured in your GitHub repository before deploying

4. **Review Access Permissions** - Limit repository access and deploy keys to only necessary personnel

### Files That Should Never Be Committed

The following files contain sensitive information and are excluded via `.gitignore`:
- `.env` and `.env.*` files
- `*.json` files (except package.json/tsconfig.json)
- `*.key`, `*.pem`, `*.p12`, `*.pfx` files (private keys/certificates)
- `secrets/` directory
- `local_config.py`

## Credential Rotation Schedule

It's recommended to rotate credentials periodically:
- API Keys: Every 90 days
- Database credentials: Every 180 days
- Service account keys: Every 90 days

## Reporting Security Issues

If you discover a security vulnerability, please email [CONTACT_EMAIL] with details. Do not open a public issue.
