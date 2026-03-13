# import pandas as pd
# from sqlalchemy import create_engine
# import os
# DB_PATH = r"c:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\healthcare_data.db"
# print(f"Using database at: {DB_PATH}")

# engine = create_engine(f'sqlite:///{DB_PATH}')

# # Example: Query all rows from user_metrics table
# df = pd.read_sql('SELECT Pregnancy FROM Dataset1 where Patient_Number=1', engine)
# print(df)


from vectorDB import user_query
response = user_query(query_texts="What is the age of Patient_Number: 1?", n_results=1, where = {'source_dataset': {"$in": ["Dataset2"]}}, where_document=None, include=["documents", "metadatas"])
print(response)