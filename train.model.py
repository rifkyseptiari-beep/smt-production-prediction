# ==========================================
# train_model.py
# Klasifikasi Produk Good dan Defect
# Menggunakan Decision Tree
# ==========================================

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# ==========================================
# Membaca Dataset
# ==========================================

df = pd.read_excel("dataset_smt_production_1000.xlsx")

print("===== DATASET =====")
print(df.head())

# ==========================================
# Data Preprocessing
# ==========================================

label_encoders = {}

categorical_columns = [
    "Component_Type",
    "Solder_Quality",
    "AOI_Result",
    "SPI_Result"
]

for col in categorical_columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

target_encoder = LabelEncoder()
df["Label"] = target_encoder.fit_transform(df["Label"])

# ==========================================
# Menentukan Feature dan Target
# ==========================================

X = df.drop(columns=["ID", "Label"])

y = df["Label"]

# ==========================================
# Membagi Dataset
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ==========================================
# Membuat Model Decision Tree
# ==========================================

model = DecisionTreeClassifier(
    criterion="gini",
    max_depth=5,
    random_state=42
)

model.fit(X_train, y_train)

# ==========================================
# Prediksi
# ==========================================

y_pred = model.predict(X_test)

# ==========================================
# Evaluasi
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    average="weighted"
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted"
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted"
)

print("\n==============================")
print("HASIL EVALUASI MODEL")
print("==============================")

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")

print("\nConfusion Matrix")

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(5,4))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Defect", "Good"],
    yticklabels=["Defect", "Good"]
)

plt.title("Confusion Matrix")
plt.xlabel("Prediksi")
plt.ylabel("Aktual")

# Simpan ke folder static
plt.savefig("static/confusion_matrix.png")
plt.close()

print(cm)

print("\nClassification Report")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=target_encoder.classes_
    )
)

# ==========================================
# Simpan Model
# ==========================================

joblib.dump(model, "model.pkl")

joblib.dump(label_encoders, "label_encoder.pkl")

joblib.dump(target_encoder, "target_encoder.pkl")

print("\nModel berhasil disimpan.")
print("File : model.pkl")
print("File : label_encoder.pkl")
print("File : target_encoder.pkl")