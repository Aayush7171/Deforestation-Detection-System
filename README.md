# 🌍 Deforestation Detection System

> An intelligent satellite-based system to detect and monitor deforestation using Google Earth Engine and real-time satellite imagery analysis.

![Badge](https://img.shields.io/badge/Python-3.11-blue)
![Badge](https://img.shields.io/badge/Flask-3.0-green)
![Badge](https://img.shields.io/badge/Earth%20Engine-Latest-orange)
![Badge](https://img.shields.io/badge/License-MIT-red)

## 🔗 Quick Links

- 🌐 **[Live Frontend](https://deforestation-detection-system.vercel.app/)** (Vercel)
- 🔧 **[Live Backend API](https://deforestation-detection-system.onrender.com/)** (Render)
- 📚 **[GitHub Repository](https://github.com/Aayush7171/Deforestation-Detection-System)**

## 📸 Screenshot

```
Interactive map with rectangle selection
↓
Choose before/after time periods
↓
Analyze satellite imagery (Sentinel-2)
↓
Get deforestation percentage with color-coded results
```

## ✨ Features

- 🗺️ **Interactive Map**: Draw rectangles to select analysis areas
- 📡 **Satellite Imagery**: Real-time Sentinel-2 imagery from Google Earth Engine
- 📊 **Vegetation Analysis**: NDVI (Normalized Difference Vegetation Index) calculation
- 🔍 **Deforestation Detection**: Compare vegetation between two time periods
- 📈 **Color-Coded Results**: 
  - 🟢 Green: <5% loss (Low)
  - 🟡 Yellow: 5-15% loss (Moderate)
  - 🔴 Red: >15% loss (High)
- ⚡ **Real-time Processing**: Fast analysis with cloud filtering
- 📱 **Responsive Design**: Works on desktop and mobile
- 🚀 **Production Ready**: Deployed on Render & Vercel

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Geospatial Analysis**: Google Earth Engine
- **ML Model**: TensorFlow (model.h5)
- **Server**: Gunicorn
- **Database**: Optional PostgreSQL integration

### Frontend
- **Mapping**: Leaflet.js with Leaflet Draw
- **Styles**: Modern CSS with gradients and animations
- **Hosting**: Vercel
- **Responsive**: Mobile-first design

### Deployment
- **Backend**: Render (Python/Flask)
- **Frontend**: Vercel (Static hosting)
- **Authentication**: Google Earth Engine service account

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Earth Engine account
- npm (for frontend only)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/deforestation-detection.git
cd deforestation-detection
```

2. **Setup Backend**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Authenticate with Earth Engine
earthengine authenticate
```

3. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Add your Earth Engine project ID
```

4. **Run Development Server**
```bash
python app.py
```

Visit: `http://localhost:5000`

## 📖 Usage

1. **Select Area**: Draw a rectangle on the satellite map
2. **Choose Periods**: 
   - **Before Period**: Earlier time range
   - **After Period**: Later time range
3. **Analyze**: Click the "Analyze" button
4. **View Results**: See deforestation percentage and status

### Example
- Before: January 2023 - June 2023
- After: June 2023 - December 2023
- Result: X% vegetation loss detected

## 🔄 How It Works

```
1. User selects area (coordinates)
2. Fetches Sentinel-2 satellite images
3. Filters for <20% cloud coverage
4. Calculates NDVI for both periods
   NDVI = (NIR - RED) / (NIR + RED)
5. Compares vegetation percentages
6. Calculates loss: (Before - After) / Before * 100%
7. Returns result with status
```

## 📊 API Endpoints

### `POST /calculate`
Analyze deforestation in selected area

**Request:**
```json
{
  "coords": [west, south, east, north],
  "start1": "2023-01-01",
  "end1": "2023-06-01",
  "start2": "2023-06-01",
  "end2": "2023-12-31"
}
```

**Response (Success):**
```json
{
  "deforestation": 12.45
}
```

**Response (Error):**
```json
{
  "error": "No satellite images found for selected dates"
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "deforestation-detection"
}
```

## 🌐 Live Deployment

✅ **Frontend (Vercel)**: https://deforestation-detection-system.vercel.app/

✅ **Backend API (Render)**: https://deforestation-detection-system.onrender.com/

Both are **LIVE and Production Ready**! 🚀

### Quick Deploy to Render & Vercel

**Backend (Render):**
```bash
git push origin main
# Render auto-deploys
# Visit: https://deforestation-detection-system.onrender.com
```

**Frontend (Vercel):**
```bash
# Connected to GitHub
# Auto-deploys on push
# Visit: https://deforestation-detection-system.vercel.app
```

## ⚙️ Configuration

### Environment Variables

```env
# Earth Engine
EE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Flask
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

## 🧪 Testing

### Local Testing
```bash
# Test endpoint
curl http://localhost:5000/health

# Test with sample data (manually)
# See test_request.sh for example
```

### Production Testing
```bash
# Check deployment
curl https://deforestation-detection.onrender.com/health
```

## 📁 Project Structure

```
deforestation-detection/
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── Procfile                  # Render deployment
├── runtime.txt              # Python version
├── wsgi.py                  # WSGI entry point
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── DEPLOYMENT.md            # Deployment guide
├── README.md                # This file
├── templates/
│   └── index.html          # Main frontend
├── static/
│   └── style.css           # Styling
└── model.h5                 # ML model (optional)
```

## 🎨 Customization

### Change Colors
Edit `static/style.css`:
```css
.header {
    background: linear-gradient(to right, #color1, #color2);
}
```

### Adjust NDVI Threshold
Edit `app.py`:
```python
vegetation = ndvi.gt(0.3)  # Change 0.3 to different threshold
```

### Modify Status Ranges
Edit `templates/index.html`:
```javascript
function getStatusColor(deforestation) {
    if (deforestation < 5) return "success";  // Adjust thresholds
    if (deforestation < 15) return "warning";
    return "danger";
}
```

## 🐛 Troubleshooting

### Earth Engine Issues
- Verify service account credentials
- Check project ID matches authentication
- Ensure API is enabled in Google Cloud

### No Results
- Date range may lack satellite data
- Cloud coverage too high
- Area may be outside Sentinel-2 coverage

### Slow Response
- Large areas take longer
- Cloud filtering reduces available images
- Check Earth Engine API quota

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting.

## 📚 Resources

- [Google Earth Engine](https://earthengine.google.com/)
- [Sentinel-2 Info](https://www.esa.int/Applications/Observing_the_Earth/Sentinel-2)
- [NDVI Calculation](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index)
- [Leaflet Documentation](https://leafletjs.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Aayush** - GreenSkills & AI Project

## 🌱 Environmental Impact

This tool helps monitor and combat deforestation by providing accessible, real-time forest change detection. Together, we can protect our planet! 🌍

---

**Made with ❤️ for the environment**

⭐ If you found this useful, please star the repository!
