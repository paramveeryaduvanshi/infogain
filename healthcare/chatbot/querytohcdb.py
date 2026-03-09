import pandas as pd
from sqlalchemy import create_engine
import os
DB_PATH = r"c:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\healthcare_data.db"
print(f"Using database at: {DB_PATH}")

engine = create_engine(f'sqlite:///{DB_PATH}')

# Example: Query all rows from user_metrics table
df = pd.read_sql('SELECT Pregnancy FROM Dataset1 where Patient_Number=1', engine)
print(df)