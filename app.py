from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from whitenoise import WhiteNoise
import ee
import os
from dotenv import load_dotenv
import logging
import json
import tempfile
import base64

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
        # Method 1: Try using local credentials.json file
        creds_file = os.path.join(BASE_DIR, 'credentials.json')
        if os.path.exists(creds_file):
            try:
                credentials = ee.ServiceAccountCredentials(None, creds_file)
                ee.Initialize(credentials)
                ee_initialized = True
                logger.info("✅ Earth Engine initialized with local credentials.json")
                return
            except Exception as local_creds_error:
                logger.warning(f"⚠️ Local credentials.json auth failed: {str(local_creds_error)[:100]}")
        
        # Method 2: Try using base64 encoded credentials from environment variable
        creds_base64 = os.getenv('EE_CREDENTIALS_BASE64')
        if creds_base64:
            try:
                # Decode base64
                creds_json = base64.b64decode(creds_base64).decode('utf-8')
                creds_dict = json.loads(creds_json)
                
                # Write to temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(creds_dict, f)
                    temp_creds_file = f.name
                
                credentials = ee.ServiceAccountCredentials(None, temp_creds_file)
                ee.Initialize(credentials)
                ee_initialized = True
                logger.info("✅ Earth Engine initialized with base64 encoded credentials")
                return
            except Exception as base64_error:
                logger.warning(f"⚠️ Base64 credentials failed: {str(base64_error)[:100]}")
        
        # Method 3: Try with EE_PROJECT_ID
        ee_project = os.getenv('EE_PROJECT_ID')
        if ee_project:
            try:
                ee.Initialize(project=ee_project)
                ee_initialized = True
                logger.info("✅ Earth Engine initialized with project credentials")
                return
            except Exception as project_error:
                logger.warning(f"⚠️ Project credentials failed: {str(project_error)[:100]}")
        
        # Method 4: Last resort - try cached credentials
        ee.Initialize()
        ee_initialized = True
        logger.info("✅ Earth Engine initialized with cached credentials")
        
    except Exception as final_error:
        logger.error(f"❌ Earth Engine not available: {str(final_error)[:100]}")
        ee_initialized = False

# Call initialization
initialize_earth_engine()


def get_image(area, start, end):
    """Get median composite image with optimized memory usage"""
    try:
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(area)
            .filterDate(start, end)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
            .select(['B4','B8'])
        )

        # Check collection size without loading all data
        size_reduction = collection.size()
        
        if size_reduction.getInfo() == 0:
            raise Exception("No satellite images found for selected dates")

        # Return median with optimized processing
        return collection.median()
    except Exception as e:
        logger.error(f"Error fetching satellite image: {str(e)[:100]}")
        raise


def vegetation_percent(ndvi, area):
    """Calculate vegetation percentage with optimized memory usage"""
    try:
        # Create vegetation mask
        vegetation = ndvi.gt(0.3)

        # Reduce region with lower pixel limit to save memory
        stats = vegetation.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=area,
            scale=100,  # Increased from 30m to 100m resolution (3x less memory)
            maxPixels=1e6,  # Reduced from 1e9 to 1e6
            bestEffort=True  # Use best effort if region too large
        )

        value = stats.get('nd').getInfo()

        if value is None:
            return 0

        return value * 100
    except Exception as e:
        logger.error(f"Error calculating vegetation: {str(e)[:100]}")
        raise


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
            error_msg = "Earth Engine not initialized. Please set EE_CREDENTIALS_BASE64 environment variable with your base64-encoded service account key."
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 503
        
        logger.info("Request received - processing deforestation analysis")

        data = request.get_json()

        coords = data["coords"]
        start1 = data["start1"]
        end1 = data["end1"]
        start2 = data["start2"]
        end2 = data["end2"]

        logger.info(f"Coordinates: {coords}")
        logger.info(f"Dates: {start1} to {end1} and {start2} to {end2}")

        result = calculate_deforestation(coords, start1, end1, start2, end2)

        logger.info(f"Analysis complete - Deforestation rate: {result}%")

        return jsonify({"deforestation": result})

    except TimeoutError as e:
        error_msg = f"Request timeout: Analysis took too long. Try a smaller area or shorter date range. Details: {str(e)[:100]}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 504
    except MemoryError as e:
        error_msg = f"Out of memory: Area or date range is too large. Try a smaller selection. Details: {str(e)[:100]}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 503
    except Exception as e:
        error_msg = f"Analysis error: {str(e)[:200]}"
        logger.error(f"Calculation error: {error_msg}")
        return jsonify({"error": error_msg}), 400

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    port = int(os.getenv('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)