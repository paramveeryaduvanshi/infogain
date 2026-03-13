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
        row_dict['source_dataset'] = dataset_name
        doc_text = f"Dataset: {dataset_name}, " + ", ".join([f"{col}: {val}" for col, val in row_dict.items()])
        # Generate a unique ID for this record
        unique_id = f"{dataset_name}_Patient_Number_{row_dict.get('Patient_Number', uuid.uuid4())}_{uuid.uuid4().hex[:6]}"
        
        metadata = row_dict  # You can customize metadata as needed, here we are using the entire row as metadata
        #metadata = sanitize_metadata(metadata)  # If you have a function to clean/sanitize
        ids.append(unique_id)
        documents.append(doc_text)
        metadatas.append(metadata)
    # Call your specific function
    add_documents(ids, documents, metadatas)    
    print(f"✅ Successfully pushed {len(documents)} records from {dataset_name}")

# Run for both datasets
process_and_push(df1, "Dataset1")


def process_and_push_in_chunks(df, dataset_name):
    chunk_size = 10
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        # Combine all rows into one document string
        doc_text = "\n".join([
            ", ".join([f"{col}: {val}" for col, val in row.items()])
            for _, row in chunk.iterrows()
        ])
        unique_id = f"{dataset_name}_Patient_Number_{i+1}_{uuid.uuid4().hex[:6]}"
        # You can choose what metadata to keep for the chunk
        metadata = {
            "source_dataset": dataset_name,
            "Patient_Numbers": i+1
        }
        add_documents(unique_id, documents=[doc_text], metadatas=[metadata])
    #print(unique_id,doc_text,metadata)
    print(f"✅ Successfully pushed {len(df)} records from {dataset_name} (chunk {i//chunk_size + 1})")

process_and_push_in_chunks(df2, "Dataset2")