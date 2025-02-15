from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
import os
from typing import List, Dict
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure maximum file size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class RekognitionTextExtractor:
    def __init__(self, image_bin: bytes) -> None:
        self.client = boto3.client(
            "rekognition",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        self.image_data = image_bin

    def extract_text(self) -> List[Dict]:
        try:
            response = self.client.detect_text(Image={"Bytes": self.image_data})

            return [
                {
                    "text": detection["DetectedText"],
                    "confidence": detection["Confidence"],
                    "position": detection["Geometry"]["BoundingBox"],
                }
                for detection in response["TextDetections"]
                if detection["Type"] == "LINE"
            ]

        except ClientError as e:
            logger.error(f"AWS Error: {e.response['Error']['Message']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from uploaded image using AWS Rekognition
    
    Expected input: multipart/form-data with an 'image' file
    Returns: JSON with extracted text and metadata
    """
    try:
        # Check if image file is present in request
        if 'image' not in request.files:
            return jsonify({
                "error": "No image file provided",
                "details": "Request must include an image file"
            }), 400
        
        file = request.files['image']
        
        # Check if a file was actually selected
        if file.filename == '':
            return jsonify({
                "error": "No selected file",
                "details": "A file must be selected"
            }), 400
            
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type",
                "details": f"Allowed file types are: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400

        # Read the file
        image_bytes = file.read()
        
        # Create extractor and process image
        extractor = RekognitionTextExtractor(image_bytes)
        results = extractor.extract_text()
        #summary=parseHTML(results[0]["text"])
        # Return results
        return jsonify({
            "status": "success",
            "detected_items": len(results),
            "results": results
        }), 200

    except ClientError as e:
        logger.error(f"AWS Error: {str(e)}")
        return jsonify({
            "error": "AWS Service Error",
            "details": str(e)
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    # Check for required environment variables
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        exit(1)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)