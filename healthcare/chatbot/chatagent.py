import sqlite3
#import ollama
import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.history import RunnableWithMessageHistory
from chatbot.chathistory import get_session_history
from chatbot.database_schema import metadata_structure
from chatbot.prompt import level1_query_prompt, level2_query_prompt
from dotenv import load_dotenv
import time
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# load API key (support multiple env var names)
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

DB_PATH = r"c:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\healthcare_data.db"


def get_schema():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        schema = {}
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [row[1] for row in cursor.fetchall()]
            schema[table] = columns
        conn.close()
        return schema
    except Exception as e:
        logging.error("Error fetching database schema: %s", e)
        return str(e)

def run_sql(sql_query):
    try:
        start_time = time.perf_counter()
        conn = sqlite3.connect(DB_PATH)
        # Using a Row factory makes it easy to convert to dictionaries
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()    
    
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries first
        rows_list = [dict(row) for row in rows]
        
        # Identify patient key field (common names: patient_id, PatientID, id, name)
        patient_key = None
        if rows_list:
            row_keys = rows_list[0].keys()
            for candidate in ['Patient_Number','PatientID', 'patient_id', 'Patient_ID', 'id', 'name']:
                if candidate in row_keys:
                    patient_key = candidate
                    break
        
        # Build nested dictionary: {Patient1: {attributes}}
        if patient_key:
            User_info = {}
            for row in rows_list:
                patient_id = row.pop(patient_key)  # Remove patient_key from attributes
                patient_name = f"Patient{patient_id}" if isinstance(patient_id, int) else patient_id
                User_info[patient_name] = row
        else:
            # Fallback: if no patient key found, use original list
            User_info = rows_list
        
        #print("Patient data retrieved:", User_info)
        end_time = time.perf_counter()
        logging.info(f"SQL query executed in {(end_time - start_time):.2f} seconds")
        return User_info
    except Exception as e:
        logging.error("Error executing SQL query: %s", e)
        return str(e)
    finally:
        conn.close()

def level1(user_query, schema, prompt, session_id, chat_history):
    try:
        start_time = time.perf_counter()
        ## ollama.generate() returns a GenerateResponse object
        #response = ollama.generate(model='llama3.2', prompt=prompt)
        
        ## Access the .response attribute (not dict key)
        #response_text = response.response.strip()
        llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
        level1 = RunnableSequence(prompt, llm)
        # 1. Wrap it with history management
        level1_with_history = RunnableWithMessageHistory(
            level1,
            get_session_history,
            input_messages_key="user_query",
            history_messages_key="chat_history")        
        # 2. Invoke Intent Analysis with Session ID
        config = {"configurable": {"session_id": session_id}}
        response = level1_with_history.invoke(
            {"user_query": user_query, "schema": schema, "chat_history": chat_history}, 
            config=config)
        response = response.content if hasattr(response, 'content') else response
        #logging.info(f"Level 1 Response: {response}")
        response = json.loads(response) if isinstance(response, str) else response
        if "Answer" in response.keys():
            logging.info(f"Level 1 Chat_history: {chat_history}")
        end_time = time.perf_counter()
        logging.info(f"Total processing time for level 1: {(end_time - start_time):.2f} seconds")
        return response
        
    except Exception as e:
        logging.error("Error at level1: %s", e)
        return str(e)

def level2(user_query,user_data, prompt, session_id, chat_history):    
    try:
        start_time = time.perf_counter()
        user_data =  json.dumps(user_data)
        llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
        level2 = RunnableSequence(prompt, llm)
        # 1. Wrap it with history management
        level2_with_history = RunnableWithMessageHistory(
            level2,
            get_session_history,
            input_messages_key="user_data",
            history_messages_key="chat_history")        
        # 2. Invoke Intent Analysis with Session ID
        config = {"configurable": {"session_id": session_id}}
        response = level2_with_history.invoke(
            {"user_query": user_query, "user_data": user_data, "chat_history": chat_history}, 
            config=config)
        response = response.content if hasattr(response, 'content') else response
        response = json.loads(response) if isinstance(response, str) else response
        #logging.info(f"Level 2 Response: {response}")
        logging.info(f"Level 2 Chat_history: {chat_history}")
        end_time = time.perf_counter()
        logging.info(f"Total processing time for level 2: {(end_time - start_time):.2f} seconds")
        
        return response
        
    except Exception as e:
        logging.error("Error at level2: %s", e)
        return str(e)

def main_func(user_query, session_id, schema=metadata_structure, prompt1=level1_query_prompt, prompt2=level2_query_prompt):
    try:
        chat_history = get_session_history(session_id)
        if not chat_history:
            chat_history = []      
        
        level1_response = level1(user_query, schema, prompt1, session_id, chat_history)
        
        #level1_response = json.loads(level1_response)   
        if "Query" in level1_response.keys():
            sql_query_result = run_sql(level1_response["Query"])
            user_data = [level1_response, {"Query_output": sql_query_result[0]}]
            level2_response = level2(user_query, user_data, prompt2, session_id, chat_history)
            return level2_response
        
        return level1_response
    except Exception as e:
        logging.error("Error in main function: %s", e)
        return str(e)

#response = main_func("what is avg BMI?")