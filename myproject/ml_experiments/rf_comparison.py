"""
PicScan - Traditional ML Comparison: Random Forest vs CNN on CIFAR-10
=======================================================================
This trains a Random Forest classifier on the SAME CIFAR-10 dataset used
for the CNN, so you can fairly compare a classical machine learning
algorithm against your deep learning model for your report.

Why Random Forest instead of SVM?
- SVM training on 50,000 images can take hours (SVMs scale poorly to
  large datasets: roughly O(n^2) to O(n^3) with sample count).
- Random Forest trains in a few minutes on the same data and is a
  standard, respected "classical ML" baseline in comparison studies.

Requirements: pip install scikit-learn
"""

import time
import numpy as np
from tensorflow import keras
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# ---------------------------------------------------------------------------
# 1. Load CIFAR-10 (same dataset as your CNN)
# ---------------------------------------------------------------------------
(x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()

y_train = y_train.squeeze()
y_test = y_test.squeeze()

class_names = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]

print(f"Train: {x_train.shape}, Test: {x_test.shape}")

# ---------------------------------------------------------------------------
# 2. Flatten images into feature vectors
# ---------------------------------------------------------------------------
x_train_flat = x_train.reshape(x_train.shape[0], -1).astype("float32") / 255.0
x_test_flat = x_test.reshape(x_test.shape[0], -1).astype("float32") / 255.0

print(f"Flattened train shape: {x_train_flat.shape}")
print(f"Flattened test shape: {x_test_flat.shape}")

# ---------------------------------------------------------------------------
# 3. Train Random Forest
# ---------------------------------------------------------------------------
print("\nTraining Random Forest... this may take a few minutes.")
start_time = time.time()

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    n_jobs=-1,
    random_state=42,
    verbose=1,
)

rf_model.fit(x_train_flat, y_train)

train_time = time.time() - start_time
print(f"\nTraining completed in {train_time:.1f} seconds.")

# ---------------------------------------------------------------------------
# 4. Evaluate on the test set
# ---------------------------------------------------------------------------
y_pred = rf_model.predict(x_test_flat)
rf_accuracy = accuracy_score(y_test, y_pred)

print("\n====================================")
print("RANDOM FOREST RESULTS")
print("====================================")
print(f"Test Accuracy: {rf_accuracy * 100:.2f}%")
print("\nDetailed classification report:")
print(classification_report(y_test, y_pred, target_names=class_names))

# ---------------------------------------------------------------------------
# 5. Comparison summary (fill in your CNN's actual result here)
# ---------------------------------------------------------------------------
CNN_TEST_ACCURACY = 87.32  # <-- replace with your CNN's actual test accuracy

print("\n====================================")
print("CNN vs RANDOM FOREST COMPARISON")
print("====================================")
print(f"CNN (deep learning) test accuracy:      {CNN_TEST_ACCURACY:.2f}%")
print(f"Random Forest (classical ML) accuracy:  {rf_accuracy * 100:.2f}%")
print(f"Difference:                              {CNN_TEST_ACCURACY - rf_accuracy * 100:.2f} percentage points")