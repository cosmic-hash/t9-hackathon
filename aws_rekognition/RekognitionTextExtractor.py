import boto3
from botocore.exceptions import ClientError
import os
from typing import List, Dict


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
        """
        Extract text from image without storing any data

        Returns:
            List of detected text with confidence scores

        Example Response:
            [
                {
                    'text': 'ABC123',
                    'confidence': 98.5,
                    'position': {
                        'left': 0.25,
                        'top': 0.30,
                        'width': 0.40,
                        'height': 0.15
                    }
                }
            ]
        """
        try:
            response = self.client.detect_text(Image={"Bytes": self.image_data})

            return [
                {
                    "text": detection["DetectedText"],
                    "confidence": detection["Confidence"],
                    "position": detection["Geometry"]["BoundingBox"],
                }
                for detection in response["TextDetections"]
                if detection["Type"] == "LINE"  # Filter for complete lines
            ]

        except ClientError as e:
            print(f"AWS Error: {e.response['Error']['Message']}")
            return []
        except FileNotFoundError:
            print("Error: Image file not found")
            return []


if __name__ == "__main__":
    # Create .env file with:
    # AWS_ACCESS_KEY_ID=YOUR_KEY
    # AWS_SECRET_ACCESS_KEY=YOUR_SECRET
    # AWS_REGION=your-region

    extractor = RekognitionTextExtractor()
    results = extractor.extract_text("pill_image.jpg")

    print("Detected Text:")
    for item in results:
        print(f"- {item['text']} (Confidence: {item['confidence']:.1f}%)")
        print(f"  Position: {item['position']}")
