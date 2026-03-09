import sqlite3
import ollama
import os
import json
import logging

DB_PATH = r"c:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\healthcare_data.db"

def get_schema():
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

def llm_generate_sql(user_query, schema):
    # Updated prompt to strictly output JSON only (no extra text)
    prompt = f"""
    You are a SQL query generator.
    Based on the following database schema and user query, generate an appropriate SQL query.
    If the user_query does not require a SQL query, respond with "None"
    
    Database schema: {schema}
    User query: "{user_query}"
    
    Output ONLY valid JSON: {{"SQLquery": "your generated SQL query here"}} or {{"SQLquery": "None"}} if no SQL is needed.
    Do not include any extra text, explanations, or formatting outside the JSON.
    """
    
    try:
        # ollama.generate() returns a GenerateResponse object
        response = ollama.generate(model='llama3.2', prompt=prompt)
        
        # Access the .response attribute (not dict key)
        response_text = response.response.strip()
        
        logging.debug("LLM response: %s", response_text)
        
        # Parse the JSON response
        parsed = json.loads(response_text)
        sql_query = parsed.get('SQLquery', 'None').strip()
        
        return sql_query
        
    except json.JSONDecodeError as e:
        logging.error("Failed to parse LLM response as JSON: %s", e)
        return "None"
    except Exception as e:
        logging.error("Error generating SQL: %s", e)
        return "None"

def run_sql(sql_query):
    conn = sqlite3.connect(DB_PATH)
    # Using a Row factory makes it easy to convert to dictionaries
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    try:
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
        
        return User_info
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

def agent(user_query):
    print("Generating SQL query for user query:", user_query)
    schema = get_schema()
    print("Database schema retrieved:", schema)
    sql_query = llm_generate_sql(user_query, schema)
    print("Generated SQL query:", sql_query)
    if sql_query.strip().lower() == "none":
        return {"User_info": None}
    result = run_sql(sql_query)
    print("Query result:", result)  
    return result

# response = agent("Compare health status of patient 1 and 2")
# print("Final response from agent:", response)