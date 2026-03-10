# 🚀 Deployment Checklist & Quick Reference

## Pre-Deployment Checklist

### ✅ Code Preparation
- [ ] All code committed to GitHub
- [ ] `.gitignore` includes `.env`, `credentials.json`, `__pycache__`
- [ ] `requirements.txt` updated with all dependencies
- [ ] README.md complete with usage instructions
- [ ] No hardcoded secrets in code

### ✅ Earth Engine Setup
- [ ] Google Cloud project created
- [ ] Earth Engine API enabled
- [ ] Service account created
- [ ] Service account has "Editor" role
- [ ] JSON credentials downloaded
- [ ] Service account registered with Earth Engine
  ```bash
  earthengine authenticate --account=your-email@gmail.com
  ```

### ✅ Local Testing
- [ ] Code runs locally without errors
- [ ] All endpoints tested
  ```bash
  curl http://localhost:5000/health
  ```
- [ ] UI renders properly in browser
- [ ] Analysis works with test area and dates

---

## Deployment Option 1: Render + Vercel (RECOMMENDED)

### Backend (Render) - ~5 minutes

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up (free tier available)

2. **Connect GitHub**
   - Click "New +" → "Web Service"
   - Select your repository
   - Authorize GitHub access

3. **Configure Service**
   ```
   Name: deforestation-detection
   Environment: Python 3.11
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **Add Environment Variables**
   ```
   EE_PROJECT_ID = your-earth-engine-project-id
   FLASK_ENV = production
   FLASK_DEBUG = False
   ```

5. **Handle Credentials**
   Option A (File):
   - Add `credentials.json` to project root
   - Add to `.gitignore`
   - Set: `GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json`
   
   Option B (Environment):
   - Encode: `base64 -i credentials.json > creds.b64`
   - Add to Render as: `EE_CREDENTIALS_B64`
   - Update app.py to decode

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)
   - Get URL: `https://deforestation-detection.onrender.com`

### Frontend (Vercel) - ~3 minutes

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up (free tier)

2. **Import Project**
   - Click "Import Project"
   - Select GitHub repository
   - Authorize GitHub

3. **Configure**
   ```
   Framework Preset: Other (static)
   Build Command: (leave empty)
   Output Directory: (leave empty)
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment
   - Get URL: `https://your-project.vercel.app`

### Test Deployment

```bash
# Test backend
curl https://deforestation-detection.onrender.com/health

# Test frontend
# Visit the Vercel URL in browser
# Draw area, set dates, click Analyze
```

---

## Deployment Option 2: Docker (Local/VPS)

### Quick Docker Deployment

```bash
# Make script executable
chmod +x docker-deploy.sh

# Run deployment script
./docker-deploy.sh

# Or manually:
docker-compose up -d
```

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop container
docker-compose stop

# Start container
docker-compose start

# Remove container
docker-compose down

# Check status
docker-compose ps
```

---

## Deployment Option 3: Traditional VPS (DigitalOcean, Linode, etc.)

### Setup Ubuntu Server

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Python, pip, nginx
apt install -y python3.11 python3-pip nginx

# Clone project
cd /var/www
git clone https://github.com/yourusername/deforestation-detection.git
cd deforestation-detection

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env  # Add your credentials

# Test Flask
python app.py  # Should start on port 5000

# Setup systemd service
sudo nano /etc/systemd/system/deforestation.service
```

Add to systemd service file:
```ini
[Unit]
Description=Deforestation Detection Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/deforestation-detection
Environment="PATH=/var/www/deforestation-detection/venv/bin"
ExecStart=/var/www/deforestation-detection/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable deforestation
sudo systemctl start deforestation
sudo systemctl status deforestation
```

Setup Nginx reverse proxy:
```bash
sudo nano /etc/nginx/sites-available/deforestation
```

---

## Environment Variables Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `EE_PROJECT_ID` | Yes | `my-earth-engine-proj` | From Google Cloud |
| `GOOGLE_APPLICATION_CREDENTIALS` | Yes* | `/app/credentials.json` | *Or use B64 encoding |
| `FLASK_ENV` | No | `production` | `development` for local |
| `FLASK_DEBUG` | No | `False` | Never `True` in production |
| `PORT` | No | `5000` | Render sets automatically |
| `FRONTEND_URL` | No | `https://app.vercel.app` | For CORS |

---

## Post-Deployment

### ✅ Verify Deployment

1. **Check Backend**
   ```bash
   # Health endpoint
   curl https://your-backend-url/health
   
   # Response should be:
   # {"status": "healthy", "service": "deforestation-detection"}
   ```

2. **Check Frontend**
   - Visit your Vercel URL
   - Verify UI loads
   - Try a test analysis

3. **Check Logs**
   - Render: Dashboard → Logs
   - Vercel: Dashboard → Functions
   - Look for any errors

### 🔒 Security Steps

1. Enable HTTPS (automatic on Render/Vercel)
2. Update CORS origins if needed
3. Rotate credentials periodically
4. Monitor API usage
5. Set up error alerts

### 📊 Monitoring

**Render Dashboard:**
- View request logs
- Monitor CPU/Memory
- Check deployment history

**Vercel Dashboard:**
- View deployment logs
- Monitor bandwidth
- Check analytics

---

## Troubleshooting

### Build Fails
```
Error: ModuleNotFoundError: No module named 'flask'
```
→ Check `requirements.txt` is in root directory

### Earth Engine Auth Error
```
Error: Earth Engine initialization failed
```
→ Verify credentials file path or env variable
→ Check service account has Earth Engine API enabled

### CORS Error
```
Access to XMLHttpRequest blocked by CORS policy
```
→ Verify frontend URL in CORS settings
→ Backend has CORS enabled already

### No Satellite Data
```
Error: No satellite images found
```
→ Try different date range
→ Area may lack Sentinel-2 coverage
→ Reduce cloud coverage threshold in code

### Slow Performance
→ Reduce analysis area size
→ Narrow date ranges
→ Check Earth Engine quota usage

---

## Cost Breakdown

| Service | Free Tier | Paid Plan |
|---------|-----------|-----------|
| **Render** | 750 hours/month | $7/month (Starter) |
| **Vercel** | 100GB bandwidth | $20/month (Pro) |
| **Google Earth Engine** | Free | Depends on usage |

---

## Useful Commands

```bash
# View all deployed services
render ls

# Check service status
render status

# View logs
render logs -f

# Restart service
render restart

# Update env variables
render env:set KEY=value
```

## Quick Links

- 🔗 [Render Documentation](https://render.com/docs)
- 🔗 [Vercel Documentation](https://vercel.com/docs)
- 🔗 [Earth Engine Guide](https://developers.google.com/earth-engine/guides)
- 🔗 [Flask Documentation](https://flask.palletsprojects.com/)
- 🔗 [Docker Documentation](https://docs.docker.com/)

---

## Support

If deployment fails:
1. Check logs carefully for error messages
2. Verify all environment variables set
3. Ensure credentials are correct
4. Check GitHub for latest issues/solutions
5. Reach out to platform support

---

**Status: Ready to Deploy! 🚀**

Choose your platform above and follow the steps. Good luck! 🌍
