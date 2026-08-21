from retriever import get_retriever


test_cases = [
    ("Where does Rohit study?", "documents\\profile.pdf"),
    ("What are Rohit's skills?", "documents\\profile.pdf"),
    ("What certifications does he have?", "documents\\profile.pdf"),
    ("What is C++?", "documents\\C++ Unit-1.pdf"),
]


retriever = get_retriever()

hits = 0


for query, expected_source in test_cases:

    results = retriever.invoke(query)

    sources = [
        document.metadata.get("source")
        for document in results
    ]

    hit = expected_source in sources

    if hit:
        hits += 1

    print("\nQuery:", query)
    print("Expected source:", expected_source)
    print("Retrieved sources:", sources)
    print("Hit:", hit)


hit_rate = hits / len(test_cases)


print("\n========== Evaluation ==========")
print("Total:", len(test_cases))
print("Hits:", hits)
print(f"Hit Rate: {hit_rate:.2%}")