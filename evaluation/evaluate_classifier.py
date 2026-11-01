
"""
TelecomCare-AI Classification Evaluation.

Evaluates ticket category and priority predictions
without calling the LLM or human approval workflow.

Metrics:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix
- Classification Report
"""

import json
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from agents.it_agent import classify_ticket


# --------------------------------------------------
# 1. LOAD EVALUATION DATASET
# --------------------------------------------------

DATASET_PATH = Path("evaluation/test_cases.json")

with DATASET_PATH.open("r", encoding="utf-8") as file:
    test_cases = json.load(file)


if not test_cases:
    raise ValueError("Evaluation dataset is empty.")


# --------------------------------------------------
# 2. STORE ACTUAL AND PREDICTED VALUES
# --------------------------------------------------

actual_categories = []
predicted_categories = []

actual_priorities = []
predicted_priorities = []

both_correct = 0

print("\n========== CLASSIFICATION EVALUATION ==========\n")


# --------------------------------------------------
# 3. RUN CLASSIFICATION TESTS
# --------------------------------------------------

for test in test_cases:

    question = test["question"]

    # Run classification only
    prediction = classify_ticket({
        "question": question
    })

    predicted_category = prediction["category"]
    predicted_priority = prediction["priority"]

    expected_category = test["expected_category"]
    expected_priority = test["expected_priority"]

    # Store actual and predicted values
    actual_categories.append(expected_category)
    predicted_categories.append(predicted_category)

    actual_priorities.append(expected_priority)
    predicted_priorities.append(predicted_priority)

    category_match = predicted_category == expected_category
    priority_match = predicted_priority == expected_priority

    if category_match and priority_match:
        both_correct += 1

    print(f"Test ID: {test['id']}")
    print(f"Question: {question}")

    print(f"Expected Category: {expected_category}")
    print(f"Predicted Category: {predicted_category}")

    print(f"Expected Priority: {expected_priority}")
    print(f"Predicted Priority: {predicted_priority}")

    print(
        "Result:",
        "PASS" if category_match and priority_match else "FAIL"
    )

    print("-" * 60)


# --------------------------------------------------
# 4. CATEGORY EVALUATION METRICS
# --------------------------------------------------

category_accuracy = accuracy_score(
    actual_categories,
    predicted_categories
)

category_precision = precision_score(
    actual_categories,
    predicted_categories,
    average="weighted",
    zero_division=0
)

category_recall = recall_score(
    actual_categories,
    predicted_categories,
    average="weighted",
    zero_division=0
)

category_f1 = f1_score(
    actual_categories,
    predicted_categories,
    average="weighted",
    zero_division=0
)


# --------------------------------------------------
# 5. PRIORITY EVALUATION METRICS
# --------------------------------------------------

priority_accuracy = accuracy_score(
    actual_priorities,
    predicted_priorities
)

priority_precision = precision_score(
    actual_priorities,
    predicted_priorities,
    average="weighted",
    zero_division=0
)

priority_recall = recall_score(
    actual_priorities,
    predicted_priorities,
    average="weighted",
    zero_division=0
)

priority_f1 = f1_score(
    actual_priorities,
    predicted_priorities,
    average="weighted",
    zero_division=0
)


# --------------------------------------------------
# 6. CONFUSION MATRICES
# --------------------------------------------------

category_labels = sorted(set(
    actual_categories + predicted_categories
))

priority_labels = sorted(set(
    actual_priorities + predicted_priorities
))

category_cm = confusion_matrix(
    actual_categories,
    predicted_categories,
    labels=category_labels
)

priority_cm = confusion_matrix(
    actual_priorities,
    predicted_priorities,
    labels=priority_labels
)


# --------------------------------------------------
# 7. PRINT EVALUATION SUMMARY
# --------------------------------------------------

total_tests = len(test_cases)

print("\n========== CATEGORY EVALUATION ==========")

print(f"Accuracy:  {category_accuracy * 100:.2f}%")
print(f"Precision: {category_precision * 100:.2f}%")
print(f"Recall:    {category_recall * 100:.2f}%")
print(f"F1-score:  {category_f1 * 100:.2f}%")


print("\n========== PRIORITY EVALUATION ==========")

print(f"Accuracy:  {priority_accuracy * 100:.2f}%")
print(f"Precision: {priority_precision * 100:.2f}%")
print(f"Recall:    {priority_recall * 100:.2f}%")
print(f"F1-score:  {priority_f1 * 100:.2f}%")


print("\n========== CATEGORY CONFUSION MATRIX ==========")

print("Labels:", category_labels)
print(category_cm)


print("\n========== PRIORITY CONFUSION MATRIX ==========")

print("Labels:", priority_labels)
print(priority_cm)


# --------------------------------------------------
# 8. DETAILED CLASSIFICATION REPORTS
# --------------------------------------------------

print("\n========== CATEGORY CLASSIFICATION REPORT ==========")

print(classification_report(
    actual_categories,
    predicted_categories,
    labels=category_labels,
    zero_division=0
))


print("\n========== PRIORITY CLASSIFICATION REPORT ==========")

print(classification_report(
    actual_priorities,
    predicted_priorities,
    labels=priority_labels,
    zero_division=0
))


# --------------------------------------------------
# 9. OVERALL EVALUATION
# --------------------------------------------------

overall_accuracy = (both_correct / total_tests) * 100

print("\n========== OVERALL EVALUATION SUMMARY ==========")

print(f"Total Test Cases: {total_tests}")
print(f"Completely Correct Predictions: {both_correct}")
print(f"Overall Accuracy: {overall_accuracy:.2f}%")

print("\nEvaluation completed!")
