# CareOrbit Deployment Guide

## Quick Start Deployment

This guide walks you through deploying CareOrbit to production using:
- **Frontend**: Vercel (free tier)
- **Backend**: Render (free/starter tier)
- **AI Services**: Azure (free credits via Imagine Cup)

---

## Prerequisites

1. **Accounts Required**:
   - GitHub account
   - Vercel account (free)
   - Render account (free)
   - Azure account (free tier + Imagine Cup credits)

2. **Azure Resources** (create these first):
   - Azure OpenAI Service with GPT-4o deployment
   - Azure AI Search (Basic tier)

---

## Step 1: Azure Setup

### 1.1 Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Create resource → Search "Azure OpenAI"
3. Create with these settings:
   - Name: `careorbit-openai`
   - Region: East US (or nearest)
   - Pricing: S0

4. After creation, go to **Keys and Endpoint**
5. Copy:
   - `Endpoint URL` → Save as `AZURE_OPENAI_ENDPOINT`
   - `Key 1` → Save as `AZURE_OPENAI_API_KEY`

6. Go to **Model Deployments** → Deploy model:
   - Model: `gpt-4o`
   - Deployment name: `gpt-4o`
   - Save deployment name as `AZURE_OPENAI_DEPLOYMENT`

### 1.2 Create Azure AI Search Resource

1. Create resource → Search "Azure AI Search"
2. Create with settings:
   - Name: `careorbit-search`
   - Pricing: Basic ($25/month)
   - Region: Same as OpenAI

3. After creation, go to **Keys**
4. Copy:
   - `URL` → Save as `AZURE_AI_SEARCH_ENDPOINT`
   - `Primary admin key` → Save as `AZURE_AI_SEARCH_KEY`

---

## Step 2: Deploy Backend to Render

### 2.1 Prepare Repository

1. Push your code to GitHub:
```bash
cd careorbit
git init
git add .
git commit -m "Initial CareOrbit MVP"
git remote add origin https://github.com/yourusername/careorbit.git
git push -u origin main
```

### 2.2 Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `careorbit-api`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Instance Type**: Starter ($7/mo) or Free
   - **Region**: Oregon (or nearest)

5. Add Environment Variables:
   ```
   ENVIRONMENT=production
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT=gpt-4o
   AZURE_AI_SEARCH_ENDPOINT=https://your-search.search.windows.net
   AZURE_AI_SEARCH_KEY=your-search-key
   JWT_SECRET=(click Generate)
   ```

6. Click **Create Web Service**

7. Wait for deployment (5-10 minutes)

8. Copy your Render URL: `https://careorbit-api.onrender.com`

### 2.3 Verify Backend

Test your API:
```bash
curl https://careorbit-api.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "agents": {
    "history": "active",
    "medication": "active",
    "care_gap": "active",
    "appointment": "active"
  }
}
```

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`

5. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://careorbit-api.onrender.com
   ```

6. Click **Deploy**

7. Wait for deployment (2-3 minutes)

8. Your app is live at: `https://careorbit.vercel.app`

---

## Step 4: Verify Full Deployment

### 4.1 Test the Application

1. Open your Vercel URL in browser
2. You should see the CareOrbit dashboard
3. Test these features:
   - ✅ Dashboard loads with demo patient
   - ✅ Medications tab shows 5 medications
   - ✅ Appointments tab shows upcoming visits
   - ✅ Care Gaps tab shows 4 gaps
   - ✅ AI Assistant responds to messages

### 4.2 Test AI Chat

Try these messages:
- "What medications am I taking?"
- "When is my next appointment?"
- "What care gaps need attention?"

You should receive intelligent, contextual responses.

---

## Troubleshooting

### Backend Issues

**Problem**: API returns 500 errors
**Solution**: Check Render logs for Azure credential issues

**Problem**: AI responses are generic
**Solution**: Verify Azure OpenAI credentials are correct

**Problem**: Slow response times
**Solution**: Render free tier has cold starts; upgrade to Starter

### Frontend Issues

**Problem**: "Failed to fetch" errors
**Solution**: Check NEXT_PUBLIC_API_URL is set correctly

**Problem**: CORS errors in console
**Solution**: Backend CORS config needs your Vercel domain

### Azure Issues

**Problem**: "Invalid API key" errors
**Solution**: Regenerate Azure OpenAI key and update in Render

**Problem**: Rate limit errors
**Solution**: Check Azure OpenAI quotas, request increase if needed

---

## Custom Domain Setup

### Vercel Custom Domain

1. Go to Project Settings → Domains
2. Add your domain: `app.careorbit.com`
3. Configure DNS with provided records
4. Enable HTTPS (automatic)

### Render Custom Domain

1. Go to Service Settings → Custom Domains
2. Add: `api.careorbit.com`
3. Configure DNS CNAME to Render
4. Update frontend environment variable

---

## Cost Summary

### Free Tier (MVP Demo)

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Vercel | Hobby | $0 |
| Render | Free | $0 |
| Azure OpenAI | Pay-as-you-go | ~$5-20 |
| Azure AI Search | Basic | ~$25 |
| **Total** | | **~$30-45/mo** |

### Production Ready

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Vercel | Pro | $20 |
| Render | Starter | $7 |
| Azure OpenAI | S0 | ~$50 |
| Azure AI Search | Standard | ~$75 |
| Azure PostgreSQL | Basic | ~$25 |
| **Total** | | **~$177/mo** |

### Imagine Cup Credits

- Registration: $1,000 Azure credits
- Semifinalist: $25,000 Azure credits
- This covers 9+ months of production operation

---

## Security Checklist

Before going live, verify:

- [ ] Azure credentials are in environment variables (not code)
- [ ] HTTPS is enabled on all endpoints
- [ ] CORS is restricted to your domains only
- [ ] Rate limiting is configured
- [ ] Error messages don't expose sensitive info
- [ ] Audit logging is enabled

---

## Next Steps

1. **Add Authentication**: Implement Azure Entra ID for user login
2. **Add Database**: Replace in-memory with Azure PostgreSQL
3. **Add Monitoring**: Set up Azure Application Insights
4. **Add CI/CD**: Configure GitHub Actions for automated testing

---

*Deployment guide for CareOrbit Imagine Cup 2026 submission*
