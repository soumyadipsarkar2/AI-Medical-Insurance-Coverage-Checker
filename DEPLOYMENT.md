# 🚀 Render Deployment Guide

This guide will walk you through deploying the AI Medical Insurance Coverage Checker to Render.

## 📋 Prerequisites

Before deploying, make sure you have:

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/)
3. **Pinecone API Key**: Get one from [Pinecone](https://pinecone.io/)
4. **Render Account**: Sign up at [Render](https://render.com/)

## 🎯 Step-by-Step Deployment

### Step 1: Fork/Clone the Repository

If you haven't already, make sure your code is in a GitHub repository:

```bash
# If you need to create a new repository
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AI-Medical-Insurance-Coverage-Checker.git
git push -u origin main
```

### Step 2: Sign Up for Render

1. Go to [Render](https://render.com/)
2. Sign up with your GitHub account
3. Connect your GitHub account if prompted

### Step 3: Create a New Web Service

1. **Click "New +"** in your Render dashboard
2. **Select "Web Service"**
3. **Connect your GitHub repository**:
   - Choose your AI Medical Insurance Coverage Checker repository
   - Select the `main` branch

### Step 4: Configure the Service

Use these settings:

- **Name**: `ai-medical-insurance-checker`
- **Environment**: `Docker`
- **Region**: `Oregon` (or your preferred region)
- **Branch**: `main`
- **Root Directory**: `.` (leave empty)
- **Build Command**: `docker build -t ai-medical-insurance-checker .`
- **Start Command**: `docker run -p 10000:8501 ai-medical-insurance-checker`

### Step 5: Add Environment Variables

Click on "Environment" and add these variables:

#### Required Variables:
```
OPENAI_API_KEY=sk-your-openai-api-key-here
PINECONE_API_KEY=pcn-your-pinecone-api-key-here
```

#### Optional Variables (with defaults):
```
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=docsage-lite
TESSERACT_CMD=/usr/bin/tesseract
```

### Step 6: Create PostgreSQL Database

1. **Go back to dashboard** and click "New +"
2. **Select "PostgreSQL"**
3. **Configure**:
   - **Name**: `ai-medical-insurance-db`
   - **Database**: `docsage`
   - **User**: `docsage_user`
   - **Plan**: `Starter` (free tier)

### Step 7: Link Database to Web Service

1. **Go back to your web service**
2. **Click "Environment"**
3. **Add the database connection**:
   - **Key**: `DATABASE_URL`
   - **Value**: Copy the connection string from your PostgreSQL service

### Step 8: Deploy!

1. **Click "Create Web Service"**
2. **Wait for the build** (this may take 5-10 minutes)
3. **Monitor the logs** for any issues

## 🔧 Configuration Details

### render.yaml (Auto-Deployment)

The repository includes a `render.yaml` file that automates the deployment:

```yaml
services:
  - type: web
    name: ai-medical-insurance-checker
    env: docker
    plan: starter
    region: oregon
    branch: main
    buildCommand: docker build -t ai-medical-insurance-checker .
    startCommand: docker run -p 10000:8501 ai-medical-insurance-checker
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: PINECONE_API_KEY
        sync: false
      - key: PINECONE_ENVIRONMENT
        value: us-east-1-aws
      - key: PINECONE_INDEX_NAME
        value: docsage-lite
      - key: DATABASE_URL
        fromDatabase:
          name: ai-medical-insurance-db
          property: connectionString
      - key: BASE_URL
        value: https://ai-medical-insurance-checker.onrender.com
      - key: TESSERACT_CMD
        value: /usr/bin/tesseract

databases:
  - name: ai-medical-insurance-db
    databaseName: docsage
    user: docsage_user
    plan: starter
```

### Using Blueprint Deployment

If you want to use the automated blueprint:

1. **Click "New +"** in Render dashboard
2. **Select "Blueprint"**
3. **Connect your GitHub repository**
4. **Render will automatically**:
   - Create the web service
   - Create the PostgreSQL database
   - Link them together
   - Set up environment variables

## 🌐 Accessing Your App

Once deployed, your app will be available at:
```
https://ai-medical-insurance-checker.onrender.com
```

## 🔍 Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check Docker logs in Render dashboard
   - Ensure all dependencies are in requirements.txt
   - Verify Dockerfile syntax

2. **Database Connection Issues**:
   - Wait for PostgreSQL to fully initialize
   - Check DATABASE_URL environment variable
   - Verify database credentials

3. **API Key Issues**:
   - Ensure OPENAI_API_KEY is set correctly
   - Ensure PINECONE_API_KEY is set correctly
   - Check API key permissions and quotas

4. **App Not Starting**:
   - Check application logs in Render dashboard
   - Verify start command is correct
   - Ensure port 10000 is exposed

### Checking Logs:

1. **Go to your web service** in Render dashboard
2. **Click "Logs"** tab
3. **Look for error messages** and debug accordingly

## 📊 Monitoring

### Health Checks:
- Your app includes a `/health` endpoint
- Render will automatically monitor this endpoint
- If it fails, Render will restart your service

### Performance:
- Monitor response times in Render dashboard
- Check database connection pool usage
- Watch for memory/CPU usage spikes

## 🔄 Updates

To update your deployed app:

1. **Make changes** to your code
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push origin main
   ```
3. **Render will automatically** rebuild and deploy

## 💰 Costs

### Free Tier Limits:
- **Web Service**: 750 hours/month
- **PostgreSQL**: 90 days free trial
- **Bandwidth**: 100GB/month

### Paid Plans:
- **Web Service**: $7/month for always-on
- **PostgreSQL**: $7/month for persistent storage

## 🎉 Success!

Once deployed, you can:
1. **Upload insurance policy PDFs**
2. **Ask questions** about coverage
3. **Get AI-powered answers** with citations
4. **Share the URL** with others

Your AI Medical Insurance Coverage Checker is now live on the web! 🚀
