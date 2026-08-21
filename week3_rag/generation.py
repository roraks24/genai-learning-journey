from dotenv import load_dotenv
from groq import Groq

from retriever import (
    get_retriever,
    get_context,
    create_prompt,
)
from reranker import rerank


load_dotenv()


retriever = get_retriever()

client = Groq()


while True:

    print()

    query = input("Enter the prompt: ")

    if query.lower() in {"exit", "quit"}:
        break

    results = retriever.invoke(query)

    print("\n========== Retrieved chunks ==========")

    for i, document in enumerate(results, start=1):

        print(f"\nChunk {i}")
        print(document.page_content)

        print(
            f"Source: {document.metadata.get('source')}"
        )

        print(
            f"Page: {document.metadata.get('page_label')}"
        )

    reranked_result = rerank(
        results,
        query,
        top_k=3
    )

    print("\n========== Reranked chunks ==========")

    for i, item in enumerate(reranked_result, start=1):

        document = item["document"]
        score = item["score"]

        print(f"\nChunk {i}")
        print(f"Score: {score:.4f}")
        print(document.page_content)

        print(
            f"Source: {document.metadata.get('source')}"
        )

        print(
            f"Page: {document.metadata.get('page_label')}"
        )

    reranked_documents = [
        item["document"]
        for item in reranked_result
    ]

    context = get_context(
        reranked_documents
    )

    prompt = create_prompt(
        query,
        context
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    print("\nAnswer:")
    print(answer)