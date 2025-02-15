import redis
import json
from openai import OpenAI

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Initialize OpenAI client
client = OpenAI()

# Load LASA data from file
def load_lasa_data(file_path="misc/LASA.json"):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def store_lasa_content_in_redis(lasa_data):
    cache_key = "lasa:data"
    redis_client.setex(cache_key, 1800, json.dumps(lasa_data))

def generate_prompt_for_medication_match(lasa_data, medication):
    prompt = (
        f"""Here is the LASA medication data:
{json.dumps(lasa_data, indent=2)}

Please provide the name of the medication that closely resembles the provided medication: {medication}. 

If the provided medication matches one from the list, respond with the other medication from the matched pair. 

The response should only include the name of the closely matching medication."""
    )
    return prompt

def get_matching_medication_from_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

def main():
    # Load LASA data
    lasa_data = load_lasa_data()

    # Store LASA data in Redis
    store_lasa_content_in_redis(lasa_data)

    # Get medication input from user
    medication = input("Enter the medication name: ")

    # Generate prompt and get the matching medication
    prompt = generate_prompt_for_medication_match(lasa_data, medication)
    matching_medication = get_matching_medication_from_openai(prompt)

    print("Matching Medication:", matching_medication)

if __name__ == "__main__":
    main()
