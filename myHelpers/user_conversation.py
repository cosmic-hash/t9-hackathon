import redis
import json
from openai import OpenAI

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Initialize OpenAI client
client = OpenAI()

def store_content_and_question(content, question):
    # Generate a unique key for the question
    cache_key = f"question:{question}"
    
    # Prepare the prompt with instructions
    prompt = (
        f"""Here is the content:
{content}

Please answer the following question based strictly on the content provided above:
{question}"""
    )

    return prompt

def get_answer_from_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def main():
    imprint_number = "M71"
    generic_name = "Allopurinol"
    question = "what are the warnings for this pill?"

    cache_key = f"{imprint_number}:{generic_name}"
    
    cached_data = redis_client.get(cache_key)
    print("cached_data: ", cached_data)
    print("cache_key: ", cache_key)
    # Generate prompt and store in Redis
    prompt = store_content_and_question(cached_data, question)

    # Get response from OpenAI
    answer = get_answer_from_openai(prompt)

    print("Answer:", answer)

# if __name__ == "__main__":
#     main()
