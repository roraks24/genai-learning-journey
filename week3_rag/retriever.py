from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from pdfloader import pf


documents = pf()


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vector_store = FAISS.from_documents(
    documents,
    embedding_model
)


def get_retriever():
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 10
        }
    )

    return retriever


def get_context(results):
    context = []

    for i, document in enumerate(results, start=1):

        context.append(
            f"""--- Chunk {i} ---
Source: {document.metadata.get("source", "Unknown")}
Page: {document.metadata.get("page_label", "Unknown")}

{document.page_content}"""
        )

    return "\n\n".join(context)


def create_prompt(query, context):

    prompt = f"""Do not infer, assume, or add information that is not directly stated.

If the answer is not explicitly present in the context, say:
"I don't know based on the provided context."

For questions involving multiple topics:
- Answer each topic separately.
- Cover every topic represented in the context.
- Do not assume a relationship between topics unless the context explicitly states it.

Use the following context to answer the question.

Query:
{query}

Context:
{context}
"""

    return prompt