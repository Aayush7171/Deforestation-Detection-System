from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import ee
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for frontend access
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Earth Engine
try:
    # Try to authenticate with service account
    ee_project = os.getenv('EE_PROJECT_ID', 'deforestation-calculation')
    ee.Initialize(project=ee_project)
    logger.info("Earth Engine initialized successfully")
except Exception as e:
    logger.warning(f"Earth Engine initialization with service account failed: {e}")
    try:
        # Fallback to default authentication
        ee.Initialize()
        logger.info("Earth Engine initialized with default credentials")
    except Exception as auth_error:
        logger.error(f"Failed to initialize Earth Engine: {auth_error}")


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
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for deployment monitoring"""
    return jsonify({"status": "healthy", "service": "deforestation-detection"}), 200


@app.route("/calculate", methods=["POST"])
def calculate():

    try:
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