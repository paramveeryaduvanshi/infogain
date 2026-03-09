from django.http import JsonResponse
from django.shortcuts import render
import json
from .chatagent import agent
import ollama
from .prompt import health_analysis_prompt
import time

def chatbot(request):
    return render(request, 'chatbot.html')

def test(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Malformed JSON'}, status=400)

    query = data.get('query')
    if not query or not isinstance(query, str) or not query.strip():
        return JsonResponse({'error': 'No query provided'}, status=400)

    try:
        start_time = time.perf_counter()
        user_info = agent(query)
        end_time = time.perf_counter()
        print("User information", user_info)
        print("SQL processing time:", end_time - start_time)
    except Exception as exc:
        print("agent() failed")
        return JsonResponse({'error': str(exc)}, status=500)

    start_time = time.perf_counter()
    try:
        print("calling ollama.generate …")
        response = ollama.generate(
            model='llama3.2',
            prompt=health_analysis_prompt.format(
                user_info=json.dumps(user_info),
                query=query
            ),
        )
        print("ollama returned:", response)
        
        # Extract text from GenerateResponse object
        if hasattr(response, 'response'):
            # GenerateResponse has a .response attribute containing the text
            response_text = response.response
        else:
            # fallback: convert to string
            response_text = str(response)
            
    except Exception as exc:
        print("LLM call failed")
        return JsonResponse({'error': 'LLM error', 'detail': str(exc)}, status=500)
    end_time = time.perf_counter()
    print("LLM processing time: %.2f s", end_time - start_time)

    return JsonResponse({'result': response_text})
