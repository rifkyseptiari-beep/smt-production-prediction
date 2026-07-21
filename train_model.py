import pandas as pd
import mysql.connector
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

# =====================================
# Koneksi Database
# =====================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="smt_production"
)

# =====================================
# Membaca Data dari MySQL
# =====================================

query = "SELECT * FROM production_data"

df = pd.read_sql(query, db)

print(df.head())

# =====================================
# Menghapus kolom id
# =====================================

df = df.drop(columns=["id", "created_at"])

# =====================================
# Encoding Data
# =====================================

encoder = {}

for col in [
    "component_type",
    "solder_quality",
    "aoi_result",
    "spi_result",
    "label"
]:

    le = LabelEncoder()

    df[col] = le.fit_transform(df[col])

    encoder[col] = le

# =====================================
# Feature dan Target
# =====================================

X = df.drop(columns=["label"])

y = df["label"]

# =====================================
# Split Data
# =====================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,
    test_size=0.2,
    random_state=42

)

# =====================================
# Training Model
# =====================================

model = DecisionTreeClassifier(
    criterion="gini",
    max_depth=5,
    random_state=42
)

model.fit(X_train, y_train)

# =====================================
# Prediksi
# =====================================

y_pred = model.predict(X_test)

# =====================================
# Evaluasi
# =====================================

accuracy = accuracy_score(y_test, y_pred)

print()

print("==========================")

print("HASIL TRAINING")

print("==========================")

print()

print("Accuracy :", accuracy)

print()

print(classification_report(y_test, y_pred))

# =====================================
# Simpan Model
# =====================================

joblib.dump(model, "model/model.pkl")

joblib.dump(encoder, "model/encoder.pkl")

print()

print("Model berhasil disimpan.")