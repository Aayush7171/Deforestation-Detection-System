from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from whitenoise import WhiteNoise
import ee
import os
from dotenv import load_dotenv
import logging
import json
import tempfile

# Load environment variables
load_dotenv()

# Get the absolute path to the templates and static directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Initialize Flask with explicit template and static folder paths
app = Flask(__name__, 
            template_folder=TEMPLATE_DIR, 
            static_folder=STATIC_DIR,
            static_url_path='/static')

# Use WhiteNoise to serve static files efficiently
app.wsgi_app = WhiteNoise(app.wsgi_app, root=STATIC_DIR)

# Enable CORS for frontend access
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track EE initialization
ee_initialized = False

# Initialize Earth Engine (non-blocking)
def initialize_earth_engine():
    global ee_initialized
    try:
        # Check if credentials are provided as environment variable
        creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        
        if creds_json:
            # Write credentials to temporary file
            try:
                creds_dict = json.loads(creds_json)
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(creds_dict, f)
                    creds_file = f.name
                
                # Use service account credentials
                credentials = ee.ServiceAccountCredentials(None, creds_file)
                ee.Initialize(credentials)
                ee_initialized = True
                logger.info("✅ Earth Engine initialized with service account credentials")
                return
            except Exception as creds_error:
                logger.warning(f"⚠️ Service account auth failed: {str(creds_error)[:100]}")
        
        # Fallback: Try with EE_PROJECT_ID
        ee_project = os.getenv('EE_PROJECT_ID', 'deforestation-calculation')
        ee.Initialize(project=ee_project)
        ee_initialized = True
        logger.info("✅ Earth Engine initialized with project credentials")
        
    except Exception as e:
        logger.warning(f"⚠️ Earth Engine initialization failed: {str(e)[:100]}")
        try:
            # Last resort: Try with cached credentials
            ee.Initialize()
            ee_initialized = True
            logger.info("✅ Earth Engine initialized with cached credentials")
        except Exception as final_error:
            logger.error(f"❌ Earth Engine not available: {str(final_error)[:100]}")
            ee_initialized = False

# Call initialization
initialize_earth_engine()


def get_image(area, start, end):

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(area)
        .filterDate(start, end)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .select(['B4','B8'])
    )

    size = collection.size().getInfo()

    if size == 0:
        raise Exception("No satellite images found for selected dates")

    return collection.median()


def vegetation_percent(ndvi, area):

    vegetation = ndvi.gt(0.3)

    stats = vegetation.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=area,
        scale=30,
        maxPixels=1e9
    )

    value = stats.get('nd').getInfo()

    if value is None:
        return 0

    return value * 100


def calculate_deforestation(coords, start1, end1, start2, end2):

    area = ee.Geometry.Rectangle(coords)

    before = get_image(area, start1, end1)
    after = get_image(area, start2, end2)

    ndvi_before = before.normalizedDifference(['B8','B4']).rename('nd')
    ndvi_after = after.normalizedDifference(['B8','B4']).rename('nd')

    veg_before = vegetation_percent(ndvi_before, area)
    veg_after = vegetation_percent(ndvi_after, area)

    if veg_before == 0:
        return 0

    loss = ((veg_before - veg_after) / veg_before) * 100

    return round(loss,2)


@app.route("/")
def index():
    try:
        logger.info(f"Serving index.html from: {TEMPLATE_DIR}")
        logger.info(f"index.html exists: {os.path.exists(os.path.join(TEMPLATE_DIR, 'index.html'))}")
        logger.info(f"Static folder exists: {os.path.exists(STATIC_DIR)}")
        logger.info(f"style.css exists: {os.path.exists(os.path.join(STATIC_DIR, 'style.css'))}")
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index.html: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for deployment monitoring"""
    return jsonify({"status": "healthy", "service": "deforestation-detection"}), 200


@app.route("/calculate", methods=["POST"])
def calculate():

    try:
        # Check if Earth Engine is initialized
        if not ee_initialized:
            error_msg = "Earth Engine not initialized. Please set GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable with your service account key."
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 503
        
        print("Request received")

        data = request.get_json()

        coords = data["coords"]
        start1 = data["start1"]
        end1 = data["end1"]
        start2 = data["start2"]
        end2 = data["end2"]

        print("Coordinates:", coords)
        print("Dates:", start1, end1, start2, end2)

        result = calculate_deforestation(coords, start1, end1, start2, end2)

        print("Result:", result)

        return jsonify({"deforestation": result})

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Calculation error: {error_msg}")
        return jsonify({"error": error_msg}), 400

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    port = int(os.getenv('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)