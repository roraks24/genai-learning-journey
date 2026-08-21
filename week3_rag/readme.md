# Week 3 — RAG System

This folder contains my Week 3 GenAI learning work, where I built a
Retrieval-Augmented Generation pipeline from scratch and then moved
toward more advanced retrieval techniques.

## What I learned

- PDF document loading
- Recursive text splitting
- Chunk size and chunk overlap
- HuggingFace embeddings
- Document embeddings vs query embeddings
- FAISS vector search
- Similarity search
- `k`
- Distances and indices
- Threshold filtering
- Retrieval evaluation
- Context construction
- Grounded prompting
- Multi-document retrieval
- Metadata preservation
- MMR
- Relevance vs diversity
- `fetch_k`
- `lambda_mult`
- Cross-encoder reranking
- Two-stage retrieval

## Current Pipeline

Documents
→ Chunking
→ Embeddings
→ FAISS
→ Similarity Retrieval
→ Cross-Encoder Reranking
→ Context
→ Prompt
→ Groq
→ Answer

## Example

The system can answer questions about uploaded documents and return
answers grounded in the retrieved context.

It is also instructed to say:

"I don't know based on the provided context."

when the required information is not explicitly available.

## Technologies

- Python
- LangChain
- FAISS
- HuggingFace Sentence Transformers
- Cross-Encoder
- Groq API
- PyPDFLoader