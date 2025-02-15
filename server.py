from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging
from aws_rekognition.RekognitionTextExtractor import RekognitionTextExtractor
from scrape.HTMLParse import HtmlParser
import os

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

# Define allowed image file extensions for uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has one of the allowed extensions.
    Returns True if the file extension is allowed, otherwise False.
    """
    # Ensure the filename contains a period and that the extension is in the allowed set
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/health", methods=["GET"])
def health_check() -> tuple:
    """
    Basic health check endpoint to verify that the service is running.
    Returns:
        A JSON response with a status message and HTTP status code 200.
    """
    return jsonify({"status": "healthy"}), 200


@app.route("/extract_imprint", methods=["POST"])
def extract_imprint():
    """
    Endpoint to extract text from an uploaded image using AWS Rekognition.

    Expected Input:
        - A multipart/form-data POST request containing an image file with the key 'image'.

    Returns:
        - On success: A JSON response containing the extracted imprint code.
        - On error: A JSON response with an appropriate error message and HTTP status code.
    """
    try:
        # Check if the request contains a file under the key 'image'
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

        # Retrieve the file from the request
        file = request.files["image"]

        # Verify that a file was selected (filename should not be empty)
        if file.filename == "":
            return (
                jsonify(
                    {"error": "No selected file", "details": "A file must be selected"}
                ),
                400,
            )

        # Check if the file extension is allowed
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

        # Read the file's binary content
        image_bytes = file.read()

        # Initialize the RekognitionTextExtractor with the image data
        extractor = RekognitionTextExtractor(image_bytes)
        # Extract text from the image using the custom extractor
        results = extractor.extract_text()
        parser = HtmlParser(results[0]["text"])
        # Parse the content to retrieve pill information
        parser.parse_content()
        print("imprint=",results[0]["text"])

        # Return the first detected text as the imprint code in JSON format
        return (
            jsonify(
                {
                    "imprint_number": results[0]["text"],
                    "generic_name":parser.output_name,
                    "summary":parser.output_summary,
                }
            ),
            200,
        )

    except Exception as e:
        # Log any unexpected error for debugging purposes
        logger.error(f"Unexpected error: {str(e)}")
        # Return a 500 Internal Server Error response with the error details
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


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
            "generic_name":parser.output_name,
            "summary":parser.output_summary,
        }
    )


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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
