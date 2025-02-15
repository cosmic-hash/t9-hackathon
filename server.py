from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_cors import CORS
import logging
from aws_rekognition.RekognitionTextExtractor import RekognitionTextExtractor
from scrape.HTMLParse import HtmlParser
import os
import redis
from datetime import datetime
from myHelpers.openaiCall import explain_drug_from_json
from myHelpers.fdaDataProcessing import search_and_fetch_pill_info


# TODO:
# 1. Connect /extract_imprint to /get_pill_info aka pass the extracted text to get_pill_info endpoint
# 2. Implement endpoint for CHATBOT

# Load environment variables from a .env file, if available
load_dotenv()

# Configure logging: Set the logging level to INFO and create a logger for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)

# Set maximum allowed payload to 16MB (useful for limiting large file uploads)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
CORS(app)

# Directory to save images
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Define allowed image file extensions for uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def serve_frontend() -> tuple:
    """
    Serve React frontend homepage
    """
    return send_from_directory("../frontend/build", "index.html")

# @app.route('/images/<filename>')
# def serve_image(filename):
#     return send_from_directory('static/images', filename)


@app.route("/extract_imprint", methods=["POST"])
def extract_imprint():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Create dated subdirectory
        today = datetime.today().strftime("%Y-%m-%d")
        save_dir = os.path.join(app.config["UPLOAD_FOLDER"], today)
        os.makedirs(save_dir, exist_ok=True)

        # Secure filename and save
        filename = secure_filename(file.filename)
        filepath = os.path.join(save_dir, filename)
        file.save(filepath)

        # Process image
        with open(filepath, "rb") as f:
            image_bytes = f.read()

        extractor = RekognitionTextExtractor(image_bytes)
        results = extractor.extract_text()
        parser = HtmlParser(results[0]["text"])
        parser.parse_content()

        # Generate accessible URL
        image_url = "http://localhost:6969" + f"/uploads/{today}/{filename}"

        return (
            jsonify(
                {
                    "imprint_number": results[0]["text"],
                    "generic_name": parser.output_name,
                    "summary": parser.output_summary,
                    "image_url": image_url,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Add route to serve uploaded images
@app.route("/uploads/<date>/<filename>")
def serve_image(date, filename):
    try:
        return send_from_directory(
            os.path.join(app.config["UPLOAD_FOLDER"], date), filename
        )
    except FileNotFoundError:
        return jsonify({"error": "Image not found"}), 404


@app.route("/get_pill_info", methods=["POST"])
def get_pill_info():
    """
    Endpoint to retrieve pill information based on an imprint code.

    Expected Input:
        - A JSON POST request with a structure similar to:
          {
            "imprint_code": [
              {
                "text": "<imprint_code_value>"
              }
            ]
          }

    Returns:
        - On success: A JSON response containing pill details like name and description.
        - On error: A JSON response with an error message and appropriate HTTP status code.
    """
    # Attempt to parse JSON data from the request body; silent=True prevents errors if JSON is invalid
    data = request.get_json(silent=True)
    if not data or "imprint_code" not in data:
        return jsonify({"error": "Missing 'imprint_code' in JSON body"}), 400

    # Extract the value associated with 'imprint_code'
    imprint_list = data.get("imprint_code")
    # Validate that imprint_list is a non-empty list
    if not isinstance(imprint_list, list) or not imprint_list:
        return jsonify({"error": "'imprint_code' must be a non-empty list"}), 400

    # Validate that the first element in the list is a dictionary containing the key 'text'
    first_item = imprint_list[0]
    if not isinstance(first_item, dict) or "text" not in first_item:
        return (
            jsonify(
                {
                    "error": "Expected a dict with a 'text' key in the first element of 'imprint_code'"
                }
            ),
            400,
        )

    # Extract the imprint code text from the first dictionary in the list
    imprint_code: str = first_item["text"]

    # Initialize the HTML parser with the provided imprint code
    parser = HtmlParser(imprint_code)
    # Parse the content to retrieve pill information
    parser.parse_content()

    # Return the pill information as a JSON response
    return jsonify(
        {
            # Optionally include the imprint code if needed:
            "imprint_number": imprint_code,
            "generic_name": parser.output_name,
            "summary": parser.output_summary,
        }
    )


@app.route("/conversation", methods=["POST"])
def conversation():
    try:
        # Get input data
        data = request.get_json()
        imprint_number = data.get("imprint_number")
        generic_name = data.get("generic_name")
        user_query = data.get("user_query")
        not_this_pill = data.get("not_this_pill", False)
        if not imprint_number or not generic_name:
            return jsonify({"error": "Missing imprint_number or generic_name"}), 400

        # Construct cache key and fetch from Redis
        cache_key = f"{imprint_number}:{generic_name}"
        logger.info(f"Fetching data from Redis with key: {cache_key}")
        if not_this_pill:
            new_purpose, related_pill = search_and_fetch_pill_info(generic_name)
            if new_purpose:
                return jsonify(
                    {
                        "message": "Incorrect pill information detected. Fetched updated information.",
                        "generic_name": related_pill,
                        "new_purpose": new_purpose,
                    }
                )
            else:
                return (
                    jsonify(
                        {
                            "error": "No updated information found for the provided pill name."
                        }
                    ),
                    404,
                )

        pill_data = redis_client.get(cache_key)
        if not pill_data:
            return (
                jsonify(
                    {"error": "No data found for given imprint_number and generic_name"}
                ),
                404,
            )

        if not_this_pill:
            new_purpose = search_and_fetch_pill_info(generic_name)
            if new_purpose:
                return jsonify(
                    {
                        "message": "Incorrect pill information detected. Fetched updated information.",
                        "generic_name": generic_name,
                        "new_purpose": new_purpose,
                    }
                )
            else:
                return (
                    jsonify(
                        {
                            "error": "No updated information found for the provided pill name."
                        }
                    ),
                    404,
                )

        # Parse the data (assuming it's stored as JSON string)
        import json

        pill_info = json.loads(pill_data)

        # Pass the data to the OpenAI handler with optional user query
        explanation = explain_drug_from_json(pill_info, user_query)

        return jsonify(
            {
                "imprint_number": imprint_number,
                "generic_name": generic_name,
                "user_query": user_query,
                "explanation": explanation,
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error in /conversation: {str(e)}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


if __name__ == "__main__":
    # Before running the application, verify that required environment variables are set
    required_env_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        # Log an error and exit if any required environment variables are missing
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        exit(1)

    # Start the Flask application with debugging enabled (good for development)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 6969)), debug=True)
