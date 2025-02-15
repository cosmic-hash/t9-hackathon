from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging
from aws_rekognition.RekognitionTextExtractor import RekognitionTextExtractor
from scrape.HTMLParse import HtmlParser
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure maximum file size (16MB)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/health", methods=["GET"])
def health_check() -> tuple:
    """Basic health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route("/extract_imprint", methods=["POST"])
def extract_imprint():
    """
    Extract text from uploaded image using AWS Rekognition

    Expected input: multipart/form-data with an 'image' file
    Returns: JSON with extracted text and metadata
    """
    try:
        # Check if image file is present in request
        if "image" not in request.files:
            return (
                jsonify(
                    {
                        "error": "No image file provided",
                        "details": "Request must include an image file",
                    }
                ),
                400,
            )

        file = request.files["image"]

        # Check if a file was actually selected
        if file.filename == "":
            return (
                jsonify(
                    {"error": "No selected file", "details": "A file must be selected"}
                ),
                400,
            )

        # Validate file extension
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file type",
                        "details": f"Allowed file types are: {', '.join(ALLOWED_EXTENSIONS)}",
                    }
                ),
                400,
            )

        # Read the file
        image_bytes = file.read()

        # Create extractor and process image
        extractor = RekognitionTextExtractor(image_bytes)
        results = extractor.extract_text()

        # Return results
        return (
            jsonify(
                {
                    "imprint_code": results[0]["text"],
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@app.route("/get_pill_info", methods=["POST"])
def get_pill_info():
    data = request.get_json(silent=True)
    if not data or "imprint_code" not in data:
        return jsonify({"error": "Missing 'imprint_code' in JSON body"}), 400

    imprint_list = data.get("imprint_code")
    if not isinstance(imprint_list, list) or not imprint_list:
        return jsonify({"error": "'imprint_code' must be a non-empty list"}), 400

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

    imprint_code: str = first_item["text"]
    parser = HtmlParser(imprint_code)
    parser.parse_content()
    return jsonify(
        {
            # "imprint_code": parser.imprints,
            "pill_name": parser.pill_names,
            "pill_desc": parser.pill_descriptions,
        }
    )


if __name__ == "__main__":
    # Check for required environment variables
    required_env_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        exit(1)

    # Run the Flask app
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
