from django.http import JsonResponse
#from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from chatbot.prompt import intent_analysis_prompt, health_analysis_prompt
from langchain_core.runnables import RunnableSequence
from chatbot.database_schema import Database_schema
from chatbot.vectorDB import user_query
import time, json, os
from chatbot.chathistory import get_session_history
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
load_dotenv()

# load API key (support multiple env var names)
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

#llm = ChatOllama(model="mistral", temperature=0)
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

def intent_analysis(query, llm, session_id, chat_history=None):
    try:
        if chat_history is None:
            chat_history = []
        start_time = time.perf_counter()
        intent_chain = RunnableSequence(intent_analysis_prompt, llm)
        # Wrap it with history management
        chain_with_history = RunnableWithMessageHistory(
            intent_chain,
            get_session_history,
            input_messages_key="query",
            history_messages_key="chat_history",
        )

        # 2. Invoke Intent Analysis with Session ID
        config = {"configurable": {"session_id": session_id}}
        intent_response = chain_with_history.invoke(
            {"query": query, "database_schema": Database_schema, "chat_history": chat_history}, 
            config=config
        )        
        resp = intent_response.content if hasattr(intent_response, 'content') else intent_response        
        end_time = time.perf_counter()
        print(f"First LLM processing time: {(end_time - start_time):.2f} seconds")

        text = getattr(resp, "content", resp)
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        text = text.strip()

        # if LLM returns JSON text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print("Non-JSON response:", text)
            return text
    except Exception as exc:
        print("LLM call failed:", exc)
        return None

#def main_fun(query, llm, session_id, chat_history=None):
def main_fun(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    try:
        
        data = json.loads(request.body)
        query = data.get("query")
        session_id = data.get("session_id")
        chat_history = get_session_history(session_id)  # Load chat history for the session
        response = intent_analysis(query, llm, session_id, chat_history)
        #print("intent_analysis output:", response)

        if isinstance(response, dict) and list(response.keys())[0] == 'Query':
            query_text = response.get("Query")
            consolidate_documents = []
            retrieve_doc = user_query(query_texts=query_text, n_results=5, where=None, where_document=None, include=["documents", "metadatas"])
            print("Retrieve Doc from VectorDB:", retrieve_doc)
            for doc in retrieve_doc['documents']:
                consolidate_documents.append(doc)
            print("Consolidate Documents:", consolidate_documents)
            start_time = time.perf_counter()         
            
            chain = RunnableSequence(health_analysis_prompt,llm)
            # Wrap it with history management
            chain_with_history1 = RunnableWithMessageHistory(
                chain,
                get_session_history,
                input_messages_key="query_text",
                history_messages_key="chat_history",
            )

            # 2. Invoke Intent Analysis with Session ID
            config = {"configurable": {"session_id": session_id}}
            
            response = chain_with_history1.invoke(
                {"query": query, "user_info": consolidate_documents, "chat_history": chat_history}, 
                config=config
            )
            end_time = time.perf_counter()
            print(f"Second LLM processing time: {(end_time - start_time):.2f} seconds")
            print("Main func Chat_history:", chat_history)
        
        # Ensure response is JSON serializable
        if isinstance(response, dict):
            return JsonResponse(response)
        elif isinstance(response, (str, bytes)):
            return JsonResponse({'message': response})
        elif hasattr(response, 'content'):
            # If response is an object with .content, convert to string
            return JsonResponse({'message': str(response.content)})
        else:
            return JsonResponse({'message': str(response)})
    except Exception as exc:
        print("LLM call failed:", exc)
        return JsonResponse({'error': 'LLM error', 'detail': str(exc)}, status=500)