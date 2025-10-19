# API Keys Configuration Guide

This guide will help you set up all the necessary API keys for your LeniLani Lead Generation Platform.

## Required API Keys

### 1. Anthropic Claude API (Required for AI lead analysis)
- Go to: https://console.anthropic.com/
- Sign up or log in
- Navigate to API Keys section
- Create a new API key
- Copy the key and add to `backend/.env`:
  ```
  ANTHROPIC_API_KEY=sk-ant-...
  ```

### 2. Google AI (Gemini) API (Required for AI scoring)
- Go to: https://makersuite.google.com/app/apikey
- Sign in with your Google account
- Create a new API key
- Copy the key and add to `backend/.env`:
  ```
  GOOGLE_AI_API_KEY=AIza...
  ```

### 3. OpenAI API (Required for embeddings)
- Go to: https://platform.openai.com/api-keys
- Sign up or log in
- Create a new secret key
- Copy the key and add to `backend/.env`:
  ```
  OPENAI_API_KEY=sk-...
  ```

### 4. SendGrid API (Optional - for email outreach)
- Go to: https://app.sendgrid.com/
- Sign up for a free account
- Navigate to Settings > API Keys
- Create a Full Access API key
- Copy the key and add to `backend/.env`:
  ```
  SENDGRID_API_KEY=SG...
  ```
- Verify your sender email address in SendGrid

### 5. Twilio API (Optional - for SMS outreach)
- Go to: https://www.twilio.com/
- Sign up for a trial account
- Get your Account SID and Auth Token from the console
- Purchase a phone number with SMS capabilities
- Add to `backend/.env`:
  ```
  TWILIO_ACCOUNT_SID=AC...
  TWILIO_AUTH_TOKEN=...
  TWILIO_PHONE_NUMBER=+1808...
  ```

### 6. HubSpot API (Optional - for CRM integration)
- Go to: https://app.hubspot.com/
- Sign up or log in
- Navigate to Settings > Integrations > Private Apps
- Create a new private app with contacts and companies scopes
- Copy the access token and add to `backend/.env`:
  ```
  HUBSPOT_API_KEY=pat-na1-...
  ```

### 7. Firebase (Optional - for persistent storage)
- Go to: https://console.firebase.google.com/
- Create a new project or select existing
- Navigate to Project Settings > Service Accounts
- Click "Generate New Private Key"
- Save the JSON file as `backend/serviceAccountKey.json`
- Add to `backend/.env`:
  ```
  FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json
  ```

### 8. PostgreSQL with pgvector (Optional - for vector search)
- Install PostgreSQL locally or use a cloud service
- Install pgvector extension
- Create a database named `lenilani_leads`
- Add to `backend/.env`:
  ```
  DATABASE_URL=postgresql://user:password@localhost:5432/lenilani_leads
  ```

## Using Your Own Accounts

The platform is designed to use YOUR API accounts:

1. **Anthropic Account**: Uses your Claude API credits
2. **Google Account**: Uses your Google AI/Gemini credits
3. **OpenAI Account**: Uses your OpenAI credits
4. **SendGrid Account**: Sends emails from your verified domain
5. **Twilio Account**: Sends SMS from your Twilio number
6. **HubSpot Account**: Syncs leads to your HubSpot CRM
7. **Firebase Account**: Stores data in your Firebase project

## Minimum Required Setup

To get started quickly, you only need these three:

1. **ANTHROPIC_API_KEY** - For AI lead analysis and outreach generation
2. **GOOGLE_AI_API_KEY** - For lead scoring
3. **OPENAI_API_KEY** - For vector embeddings

The platform will work without the optional services, but with reduced functionality.

## Security Best Practices

1. **Never commit API keys to git**
   - The `.gitignore` file is configured to exclude `.env` files
   - Always use environment variables

2. **Rotate keys regularly**
   - Change your API keys every 90 days
   - Immediately rotate if you suspect a compromise

3. **Use different keys for development and production**
   - Create separate API keys for testing
   - Use more restrictive permissions in production

4. **Monitor usage**
   - Check your API usage dashboards regularly
   - Set up billing alerts

## Troubleshooting

### "API key not found" errors
- Verify the key is correctly set in `backend/.env`
- Ensure there are no extra spaces or quotes
- Restart the backend server after changing `.env`

### "Quota exceeded" errors
- Check your API usage limits
- Upgrade your plan if needed
- Implement rate limiting

### Email/SMS not sending
- Verify your SendGrid/Twilio account is activated
- Check that sender email/phone number is verified
- Review API credentials are correct

## Cost Estimates

With the free/starter tiers:
- **Claude API**: ~$0.015 per 1K tokens (~200 lead analyses)
- **Google AI**: Free for limited requests
- **OpenAI**: ~$0.0001 per 1K tokens for embeddings
- **SendGrid**: 100 emails/day free
- **Twilio**: $15.50 trial credit
- **HubSpot**: Free for up to 1M contacts

Estimated monthly cost for 100 leads: **~$10-20**
