from datasets import Dataset
# Example data from your RAG pipeline
data = {
    "question": ["What is the patient 1 blood pressure status?", "Is Patient ID 2 Pregnant?"],
    "answer": ["Patient 1 has abnormal blood pressure.","No, Patient ID 2 is not pregnant."],
    "contexts": [["Patient1:{'Blood_Pressure_Abnormality': 1}"], ["Patient2:{'Pregnancy': 'Yes'}"]],
    "ground_truth": ["The patient's BP is 150/95, which is classified as hypertension.", "Patient ID 2 is not pregnant."],
}

dataset = Dataset.from_dict(data)

from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

# 1. Initialize the local Ollama models
# Use a slightly larger model for evaluation (e.g., llama3.1) if possible
eval_llm = ChatOllama(model="llama3.2", temperature=0)
eval_embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 2. Wrap them for RAGAS
ragas_llm = LangchainLLMWrapper(eval_llm)
ragas_emb = LangchainEmbeddingsWrapper(eval_embeddings)


from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall

# Run the evaluation
results = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_recall],
    llm=ragas_llm,
    embeddings=ragas_emb
)

# Export to a Pandas DataFrame for easy viewing
df = results.to_pandas()
print(df[['question', 'faithfulness', 'answer_relevancy']])