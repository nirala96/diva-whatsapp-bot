# 📊 Google Sheets Setup Guide

Follow these steps to set up Google Sheets integration for the Diva Daulti AI Chatbot.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" → "New Project"
3. Enter project name: `DivaDaulti-Chatbot`
4. Click "Create"

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for and enable these APIs:
   - **Google Sheets API**
   - **Google Drive API**

## Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in details:
   - Service account name: `diva-chatbot-service`
   - Service account ID: `diva-chatbot-service` (auto-generated)
   - Description: `Service account for Diva Daulti AI Chatbot`
4. Click **Create and Continue**
5. Skip the optional steps (Grant access & Grant users access)
6. Click **Done**

## Step 4: Generate JSON Key

1. Click on the newly created service account
2. Go to the **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Click **Create**
6. A JSON file will be downloaded automatically
7. Rename it to `service_account.json`
8. Move it to your project root: `diva_ai_bot/service_account.json`

## Step 5: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Name it: `DivaDaulti_Leads`
4. (Optional) Add column headers manually:
   - Column A: `Timestamp`
   - Column B: `User`
   - Column C: `Customer Message`
   - Column D: `AI Reply`

## Step 6: Share Sheet with Service Account

This is a critical step!

1. Open the `service_account.json` file
2. Find the `client_email` field (looks like: `xxx@xxx.iam.gserviceaccount.com`)
3. Copy this email address
4. In your Google Sheet, click **Share** button
5. Paste the service account email
6. Give it **Editor** access
7. Uncheck "Notify people"
8. Click **Share**

## Step 7: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
   SHEET_NAME=DivaDaulti_Leads
   ```

## Step 8: Test the Connection

Run the sheets utility directly to test:

```bash
source venv/bin/activate
python -m utils.sheets
```

You should see:
```
Testing Google Sheets connection...
Successfully connected to Google Sheet: DivaDaulti_Leads
Added headers to Google Sheet
✓ Google Sheets integration is working correctly!
```

## Troubleshooting

### Error: "Requested entity was not found"
- Make sure you shared the sheet with the service account email
- Check that the sheet name in `.env` matches exactly

### Error: "Invalid service account credentials"
- Verify the JSON file path is correct
- Make sure the service account JSON is valid and not corrupted

### Error: "Permission denied"
- The service account needs **Editor** access to the sheet
- Re-share the sheet with proper permissions

### Error: "API not enabled"
- Make sure both Google Sheets API and Google Drive API are enabled
- Wait a few minutes after enabling (can take time to propagate)

## Security Best Practices

⚠️ **IMPORTANT**: Never commit `service_account.json` or `.env` to Git!

The `.gitignore` file is already configured to exclude these files:
```
.env
service_account.json
*.json
!pricing/*.json
```

## What Gets Logged?

Each conversation is logged with:
- **Timestamp**: When the message was received
- **User**: Phone number or identifier
- **Customer Message**: What the customer asked
- **AI Reply**: Bot's response

This allows you to:
- Track all customer interactions
- Analyze common questions
- Follow up with leads
- Monitor bot performance
- Export data for CRM

---

✅ Once completed, your chatbot will automatically log all conversations to Google Sheets!
