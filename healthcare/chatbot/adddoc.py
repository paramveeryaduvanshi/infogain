import pandas as pd
import uuid
from vectorDB import add_documents

# 1. Load your datasets
df1 = pd.read_excel(r"C:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\Health Dataset 1.xlsx")
df2 = pd.read_excel(r"C:\Users\Paramveer Singh\OneDrive\Project\infogain\healthcare\Health Dataset 2.xlsx")

def process_and_push(df, dataset_name):
    ids = []
    documents = []
    metadatas = []

    for _, row in df.iterrows():
        # Convert row to dictionary for metadata
        row_dict = row.to_dict()
        row_dict['source_dataset'] = dataset_name # Track which file it came from
        #print(row_dict) # Debug: Check the row data being processed
        # Create a descriptive string for the LLM to "read"
        # Example: "Patient 1: Age 34, BMI 23, Smoking: No..."
        doc_text = f"Dataset: {dataset_name}, " + ", ".join([f"{col}: {val}" for col, val in row_dict.items()])
        
        # Generate a unique ID for this record
        unique_id = f"{dataset_name}_Patient_Number_{row_dict.get('Patient_Number', uuid.uuid4())}_{uuid.uuid4().hex[:6]}"
        
        metadata = {
            "Patient_Number": row_dict.get("Patient_Number", "Unknown"),
            "source_dataset": dataset_name,
        }
        ids.append(unique_id)
        documents.append(doc_text)
        metadatas.append(metadata)
        print(ids, documents,metadatas)
        break
    # Call your specific function
    add_documents(ids, documents, metadatas)
    
    print(f"✅ Successfully pushed {len(documents)} records from {dataset_name}")

# Run for both datasets
process_and_push(df1, "Dataset1")
process_and_push(df2, "Dataset2")