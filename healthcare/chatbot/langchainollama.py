# from django.http import JsonResponse
# #from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI
# from chatbot.prompt import intent_analysis_prompt, health_analysis_prompt
# from langchain_core.runnables import RunnableSequence
# from chatbot.database_schema import metadata_structure
# from chatbot.vectorDB import user_query
# import time, json, os
# import logging
# from chatbot.chathistory import get_session_history
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.messages import SystemMessage
# from dotenv import load_dotenv
# load_dotenv()

# # Setup logging to display logs on console
# logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# # load API key (support multiple env var names)
# OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
# OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
# OPENAI_MODEL = os.getenv("OPENAI_MODEL")

# #llm = ChatOllama(model="mistral", temperature=0)
# llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

# def intent_analysis(query, llm, session_id, chat_history=None):
#     try:
#         if chat_history is None:
#             chat_history = []
#         start_time = time.perf_counter()
#         intent_chain = RunnableSequence(intent_analysis_prompt, llm)
#         # 1. Wrap it with history management
#         chain_with_history = RunnableWithMessageHistory(
#             intent_chain,
#             get_session_history,
#             input_messages_key="query",
#             history_messages_key="chat_history",
#         )

#         # 2. Invoke Intent Analysis with Session ID
#         config = {"configurable": {"session_id": session_id}}
#         intent_response = chain_with_history.invoke(
#             {"query": query, "metadata_structure": metadata_structure, "chat_history": chat_history}, 
#             config=config
#         )        
#         resp = intent_response.content if hasattr(intent_response, 'content') else intent_response        
#         logging.info(f"Intent Analysis Response: {resp}")
#         end_time = time.perf_counter()
#         logging.info(f"First LLM processing time: {(end_time - start_time):.2f} seconds")
#         logging.info(f"Intent func Chat_history: {chat_history}")

#         text = getattr(resp, "content", resp)
#         if isinstance(text, bytes):
#             text = text.decode("utf-8")
#         text = text.strip()

#         # if LLM returns JSON text:
#         try:
#             return json.loads(text)
#         except json.JSONDecodeError:
#             logging.info(f"Non-JSON response: {text}")
#             return text
#     except Exception as exc:
#         logging.info(f"LLM call failed: {exc}")
#         return None

# #def main_fun(query, llm, session_id, chat_history=None):
# def main_fun(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method'}, status=400)
#     try:
        
#         data = json.loads(request.body)
#         query = data.get("query")
#         session_id = data.get("session_id")
#         chat_history = get_session_history(session_id)  # Load chat history for the session
#         response = intent_analysis(query, llm, session_id, chat_history)
#         #logging.info(f"intent_analysis output: {response}")
#         if isinstance(response, str):
#             try:
#                 response = json.loads(response)
#             except Exception:
#                 print("Non-JSON response:", response)
#                 # Handle or return error here
#         if isinstance(response, dict) and "where" in response:
#             where = normalize_where(response.get("where"))
#             # logging.info(f"Generated query for VectorDB: {query_text}")
#             consolidate_documents = []
#             retrieve_doc = user_query(query_texts=query, n_results=100, where=where, where_document=None, include=["documents", "metadatas"])
#             #logging.info(f"Retrieve Doc from VectorDB: {retrieve_doc}")
#             for doc in retrieve_doc['documents']:
#                 consolidate_documents.append(doc)
#             logging.info(f"Consolidate Documents: {consolidate_documents}")
#             start_time = time.perf_counter()         
            
#             chain = RunnableSequence(health_analysis_prompt,llm)
#             # Wrap it with history management
#             chain_with_history1 = RunnableWithMessageHistory(
#                 chain,
#                 get_session_history,
#                 input_messages_key="query",
#                 history_messages_key="chat_history",
#             )

#             # 2. Invoke Intent Analysis with Session ID
#             config = {"configurable": {"session_id": session_id}}
            
#             response = chain_with_history1.invoke(
#                 {"query": query, "user_info": consolidate_documents, "chat_history": chat_history}, 
#                 config=config
#             )
#             end_time = time.perf_counter()
#             logging.info(f"Second LLM processing time: {(end_time - start_time):.2f} seconds")
#             logging.info(f"Main func Chat_history: {chat_history}")
        
#         # Ensure response is JSON serializable
#         if isinstance(response, dict):
#             return JsonResponse(response)
#         elif isinstance(response, (str, bytes)):
#             return JsonResponse({'message': response})
#         elif hasattr(response, 'content'):
#             # If response is an object with .content, convert to string
#             return JsonResponse({'message': str(response.content)})
#         else:
#             return JsonResponse({'message': str(response)})
#     except Exception as exc:
#         logging.info(f"LLM call failed: {exc}")
#         return JsonResponse({'error': 'LLM error', 'detail': str(exc)}, status=500)
# def normalize_where(where):
#     """
#     Normalize the 'where' value from LLM response to a valid dictionary for vectorDB.
#     Handles cases where 'where' is already a dict, a list of dicts, or a single value.
#     """
#     if where is None:
#         return None
#     # If it's already a dict, return as is
#     if isinstance(where, dict):
#         # Convert any dict values that are lists to $in format
#         new_where = {}
#         for k, v in where.items():
#             if isinstance(v, list):
#                 new_where[k] = {"$in": v}
#             else:
#                 new_where[k] = v
#         return new_where
#     # If it's a list of dicts, merge them (AND logic)
#     if isinstance(where, list):
#         # If it's a list of primitives, wrap in $in
#         if all(isinstance(item, (str, int, float)) for item in where):
#             return {"Patient_Number": {"$in": where}}
#         # If it's a list of dicts, merge
#         merged = {}
#         for item in where:
#             if isinstance(item, dict):
#                 merged.update(item)
#         return merged if merged else None
#     # If it's a single value, wrap in $eq
#     if isinstance(where, (str, int, float)):
#         return {"Patient_Number": {"$eq": where}}
#     logging.info(f"Unexpected 'where' format: {where}")
    
#     return {"value": where}