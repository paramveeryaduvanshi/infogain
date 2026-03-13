import logging, json
from django.http import JsonResponse
from django.shortcuts import render
from .chatagent import main_func

def chatbot(request):
    return render(request, 'chatbot.html')
def chatbot1(request):
    return render(request, 'chatbot_v1.html')

def test_chatbot(request):
    try:
        if request.method == 'POST':
            # Handle JSON or form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                user_query = data.get('query')
                session_id = data.get('session_id')
            else:
                user_query = request.POST.get('query')
                session_id = request.POST.get('session_id')
            response = main_func(user_query, session_id)
            return response
        else:
            return {"error": "Request does not have valid method"}
    except Exception as e:
        logging.info("Error in view: %s", e)
        return {"error": str(e)}



