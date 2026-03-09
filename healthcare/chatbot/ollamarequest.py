import requests
import json
def ollama_request(question,prompt):
    url = "http://localhost:11434/api/chat"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3",
        "prompt": prompt,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "stream": False,
        "max_tokens": 1000,
        "temperature": 0.2
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}"}
    
# rsponse = ollama_request("What is the capital of France?")
# print(rsponse.get("message").get("content"))