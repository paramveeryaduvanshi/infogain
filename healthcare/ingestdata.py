import pandas as pd
from sqlalchemy import create_engine
import os

# Get the directory where this script is located (healthcare folder)
DB_PATH = r"c:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\healthcare_data.db"

# 1. Load your Excel files
df_Dataset1 = pd.read_excel(r"C:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\Health Dataset 1.xlsx")
df_Dataset2 = pd.read_excel(r"C:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\Health Dataset 2.xlsx")

# # — clean nulls
# df_Dataset1.fillna(0, inplace=True)
# df_Dataset2.fillna(0, inplace=True)

# 2. Create a SQL Engine with the correct path
engine = create_engine(f'sqlite:///{DB_PATH}')

# 3. Save DataFrames to SQL Tables
df_Dataset1.to_sql('Dataset1', engine, if_exists='replace', index=False)
df_Dataset2.to_sql('Dataset2', engine, if_exists='replace', index=False)

print(f"Tables created at: {DB_PATH}")
print("Tables: Dataset1, Dataset2")

