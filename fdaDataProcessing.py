import requests
import redis
import json
from openaiCall import explain_drug_from_json
# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def load_lasa_data(file_path="misc/LASA.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("LASA data file not found.")
        return {}

def generate_openfda_url(generic_name, limit=1):
    base_url = "https://api.fda.gov/drug/label.json"
    query = f"search=openfda.generic_name:\"{generic_name}\"&limit={limit}"
    return f"{base_url}?{query}"

def fetch_fda_data(url):
    response = requests.get(url)
    print("response", response)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            purpose = results[0].get("indications_and_usage", ["Not Available"])[0]
            return purpose, data
        else:
            return None, None
    else:
        return f"Failed to fetch data. Status code: {response.status_code}", None, None, None
    
def search_and_fetch_pill_info(pill_name):
    # Load LASA data
    lasa_data = load_lasa_data()

    # Check if the pill is in the LASA mapping
    if pill_name in lasa_data:
        related_pill = lasa_data[pill_name]
        print(f"Found related pill: {related_pill}")

        # Check if the pill is in the Redis cache
        cached_data = redis_client.get(related_pill)
        if cached_data:
            print("Data fetched from cache:")
            cached_data = json.loads(cached_data)
            print(f"Purpose: {cached_data['purpose']}")
            return cached_data['purpose'], related_pill

        # If not in cache, fetch from FDA API
        url = generate_openfda_url(related_pill)
        print(f"Generated URL: {url}")
        purpose, data = fetch_fda_data(url)
        if data:
            # Store the data in Redis with a TTL of 1800 seconds (30 minutes)
            redis_client.setex(related_pill, 1800, json.dumps({"purpose": purpose, "data": data}))
            return purpose, related_pill
        else:
            print("Failed to retrieve drug information.")
            return None, None
    else:
        print("Medication not found in LASA data.")
        return None, None

def generic_fetch_summary(imprint_number, generic_name):
    url = generate_openfda_url(generic_name)
    print(f"Generated URL: {url}")

    # Fetch data from FDA API
    purpose, data = fetch_fda_data(url)
    if data:
        cache_key = f"{imprint_number}:{generic_name}"
        print("cache_key: ", cache_key)
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print("Data fetched from cache:")
            #cached_data = json.loads(cached_data)
            explanation = explain_drug_from_json(json.loads(cached_data))
            print(f"data: {explanation}")
            return explanation
        redis_client.setex(cache_key, 1800, json.dumps(data))
        explanation = explain_drug_from_json(json.dumps(data))
        return explanation
    else:
        print("Failed to retrieve drug information.")

def main():
    imprint_number = "M71"
    generic_name = "Allopurinol"

    # Generate URL
    url = generate_openfda_url(generic_name)
    print(f"Generated URL: {url}")

    # Fetch data from FDA API
    purpose, data = fetch_fda_data(url)
    if data:
        cache_key = f"{imprint_number}:{generic_name}"
        print("cache_key: ", cache_key)
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print("Data fetched from cache:")
            cached_data = json.loads(cached_data)
            # print(f"data: {cached_data}")
            return
        redis_client.setex(cache_key, 1800, json.dumps(data))
    else:
        print("Failed to retrieve drug information.")

    purpose2 = search_and_fetch_pill_info(generic_name)
    if purpose2:
        print(f"Purpose of the pill '{generic_name}': {purpose2}")
    else:
        print("No information found for the provided pill name.")

# if __name__ == "__main__":
#     main()
