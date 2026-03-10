import chromadb
# from langchain_ollama import OllamaEmbeddings
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize the high-speed ChromaDB embedding function
# This runs locally in your Python script, NO Ollama needed for this part!
embeddings_model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 2. Setup your Client and Collection

collection_name = 'healthcaseDataset'

# 1. Initialize the embedding model
#embeddings_model = OllamaEmbeddings(model="nomic-embed-text")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name=collection_name, embedding_function=embeddings_model)

def user_query(query_texts, n_results, where, where_document, include):
    #query_emb = embeddings_model.embed_query(query_texts)
    results = collection.query(
        query_texts=query_texts,
        n_results=n_results,
        where=where,
        where_document=where_document,
        include=include
        )
    return results

def add_documents(ids, documents, metadatas):
    #doc_emb = embeddings_model.embed_documents(documents)
    collection.add(
        ids=ids,
        #embeddings=doc_emb,
        documents=documents,
        metadatas=metadatas
    )

def delete_collection():
    client.delete_collection(name=collection_name)