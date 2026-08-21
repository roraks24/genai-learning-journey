from retriever import get_retriever


test_cases = [
    ("Where does Rohit study?", True),
    ("What are his skills?", True),
    ("What certifications does he have?", True),
    ("Does he love pizza?", False),
    ("What is his favorite color?", False),
]


retriever = get_retriever()


def test(test_cases):

    correct = 0
    false_positive = 0
    false_negative = 0

    for query, expected in test_cases:

        results = retriever.invoke(query)

        actual = len(results) > 0

        print("\nQuery:", query)
        print("Expected:", expected)
        print("Actual:", actual)

        if actual == expected:
            correct += 1
            print("Result: Correct")

        elif actual and not expected:
            false_positive += 1
            print("Result: False Positive")

        elif not actual and expected:
            false_negative += 1
            print("Result: False Negative")

    total = len(test_cases)

    accuracy = correct / total

    print("\n========== Evaluation ==========")
    print("Total tests:", total)
    print("Correct:", correct)
    print("False Positives:", false_positive)
    print("False Negatives:", false_negative)
    print(f"Accuracy: {accuracy:.2%}")


test(test_cases)