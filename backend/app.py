from flask import Flask, jsonify, render_template
from flask_caching import Cache
import requests
import logging

# Initialize Flask app
app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOAA API endpoint for solar wind data
NOAA_API_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"

# Function to fetch space weather data from NOAA
@cache.cached(timeout=300)  # Cache for 5 minutes
def fetch_space_weather():
    try:
        # Fetch data from NOAA API
        response = requests.get(NOAA_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Log the raw data for debugging
        logger.info(f"Raw NOAA API response: {data}")

        # Parse the data to extract the latest values
        if data and isinstance(data, list) and len(data) > 0:
            latest_entry = data[-1]  # Get the most recent data point
            logger.info(f"Latest entry: {latest_entry}")
            return {
                "timestamp": latest_entry[0],  # Timestamp
                "bt": latest_entry[1],         # Magnetic field (nT)
                "density": latest_entry[2],    # Plasma density (p/cm³)
                "speed": latest_entry[3]       # Solar wind speed (km/s)
            }
        else:
            logger.warning("No data available in NOAA API response")
            return {"error": "No data available"}

    except requests.exceptions.RequestException as e:
        # Log and handle request errors
        logger.error(f"Failed to fetch data from NOAA API: {e}")
        return {"error": "Failed to fetch data from NOAA API"}

# Route for the frontend
@app.route('/')
def home():
    return render_template('index.html')

# API endpoint for space weather data
@app.route('/api/weather')
def space_weather():
    data = fetch_space_weather()
    if "error" in data:
        # Return a 500 error if there's an issue fetching data
        return jsonify({"error": data["error"]}), 500
    return jsonify(data)

# Error handler for 404 (Page Not Found)
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404

# Error handler for 500 (Internal Server Error)
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)