# 🌍 Deforestation Detection System - Deployment Guide

A satellite-based deforestation detection system using Google Earth Engine and machine learning.

## 📋 Overview

- **Frontend**: Vercel (Static hosting)
- **Backend**: Render (Python/Flask server)
- **Data Source**: Google Earth Engine (Sentinel-2 satellite imagery)
- **Model**: TensorFlow-based vegetation analysis

---

## 🚀 Quick Deployment Steps

### **1. Backend Deployment (Render)**

#### Prerequisites
- Google Earth Engine account and service account credentials
- Render account (free tier available)
- GitHub repository with your code

#### Steps

1. **Create Render PostgreSQL Database (optional for future use)**
   - Go to [render.com](https://render.com)
   - Create new PostgreSQL database (or skip for now)

2. **Deploy Flask Backend**
   - Connect your GitHub repository to Render
   - Create new "Web Service"
   - Configure:
     - **Name**: `deforestation-detection`
     - **Environment**: Python 3.11
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

3. **Set Environment Variables in Render Dashboard**
   ```
   EE_PROJECT_ID = your-earth-engine-project-id
   FLASK_ENV = production
   FLASK_DEBUG = False
   ```

4. **Upload Earth Engine Credentials**
   - Get service account JSON from Google Cloud Console
   - Add `GOOGLE_APPLICATION_CREDENTIALS` pointing to credentials path
   - Or add credentials as environment variables

5. **Deploy**
   - Render automatically deploys on git push
   - Your backend URL will be: `https://deforestation-detection.onrender.com`

---

### **2. Frontend Deployment (Vercel)**

#### Steps

1. **Prepare Frontend for Vercel**
   ```bash
   npm init -y
   npm install
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Configure:
     - **Framework**: Other (static HTML/CSS/JS)
     - **Build Command**: Leave empty (no build needed)
     - **Output Directory**: `./`

3. **Set Environment Variables (Optional)**
   ```
   VITE_API_URL = https://deforestation-detection.onrender.com
   ```

4. **Deploy**
   - Vercel auto-deploys on push to main branch
   - Your frontend URL will be: `https://your-project.vercel.app`

---

## 🔑 Google Earth Engine Setup

### Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "Deforestation Detection"
3. Enable Earth Engine API
4. Create Service Account:
   - IAM & Admin → Service Accounts
   - Create new service account
   - Grant roles:
     - **Editor** (for Earth Engine)
     - **Service Account User**
5. Create JSON key and download
6. Register service account with Earth Engine:
   ```bash
   earthengine authenticate --quiet --account=YOUR_EMAIL
   ```

### Add Credentials to Render

Option A: Upload as file
- Add credentials.json to project
- Set `GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json`

Option B: Environment variable
- Convert JSON to base64: `base64 -i credentials.json`
- Add to Render environment as `EE_CREDENTIALS_B64`
- Update app.py to decode and use

---

## 📦 Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/deforestation-detection.git
cd deforestation-detection

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Earth Engine project ID
```

### Authenticate Earth Engine

```bash
earthengine authenticate
```

### Run Locally

```bash
python app.py
```

Visit: `http://localhost:5000`

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EE_PROJECT_ID` | Your Earth Engine project ID | `my-ee-project` |
| `FLASK_ENV` | Environment mode | `production` or `development` |
| `FLASK_DEBUG` | Debug mode | `False` (production) |
| `PORT` | Server port | `5000` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to credentials JSON | `/app/credentials.json` |

### File Structure

```
project/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── runtime.txt           # Python version
├── wsgi.py               # WSGI entry point
├── vercel.json           # Vercel config
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── templates/
│   └── index.html        # Main frontend
└── static/
    └── style.css         # Styling
```

---

## 🧪 Testing Deployment

### Check Backend Health

```bash
curl https://deforestation-detection.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "service": "deforestation-detection"}
```

### Test Full Flow

1. Visit your Vercel frontend URL
2. Draw a rectangle on the map
3. Select date ranges
4. Click "Analyze"
5. Wait for results

---

## 🐛 Troubleshooting

### Earth Engine Authentication Error
- Check Google Cloud credentials file exists
- Verify service account has Earth Engine API enabled
- Ensure project ID matches

### CORS Errors
- Frontend and backend must have correct origins
- Render backend has CORS enabled for all origins
- Check browser console for exact error

### No Satellite Data
- Date range may be too recent (Sentinel-2 has slight delay)
- Cloud coverage too high (filtered at >20%)
- Area may not have Sentinel-2 coverage
- Try different date ranges

### Slow Performance
- Large areas take longer to process
- Cloud filtering reduces available images
- Earth Engine API calls have quotas

---

## 📊 Monitoring & Logs

### View Logs

**Render Backend**:
- Dashboard → Your Service → Logs tab
- Real-time logs of API calls and errors

**Vercel Frontend**:
- Dashboard → Your Project → Functions
- See error logs and analytics

---

## 🔄 Continuous Deployment

Both Render and Vercel support auto-deployment:

1. Push code to GitHub
2. Services automatically detect changes
3. Run build commands
4. Deploy new version

No manual deployment needed!

---

## 🔐 Security Considerations

1. **Credentials**: Never commit `credentials.json`
   - Add to `.gitignore` ✓
   - Use environment variables ✓

2. **CORS**: Currently allows all origins
   - Update in production with specific domains

3. **Rate Limiting**: Implement if needed
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   ```

4. **API Keys**: Store securely in environment variables

---

## 📈 Scaling

### When to upgrade
- Render: Upgrade from Free to Starter ($7/month) if hitting limits
- Vercel: Usually fine on free tier, upgrade if exceeding bandwidth
- Earth Engine: Has usage quotas, monitor in GCP console

### Optimization
- Cache results in database
- Implement request queuing
- Add result history for users

---

## 🆘 Support & Resources

- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Earth Engine Docs](https://developers.google.com/earth-engine)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 📝 Next Steps

1. ✅ Push code to GitHub
2. ✅ Set up Render Web Service
3. ✅ Set up Vercel Project
4. ✅ Configure environment variables
5. ✅ Test deployment
6. ✅ Monitor logs and performance
7. ⭐ Share with the world!

**Happy deploying! 🚀**
