import pandas as pd
import mysql.connector

# ===============================
# Koneksi ke MySQL
# ===============================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",          # Ganti jika MySQL Anda memakai password
    database="smt_production"
)

cursor = conn.cursor()

# ===============================
# Membaca file Excel
# ===============================
df = pd.read_excel("dataset_smt_production_1000.xlsx")

print(df.head())

# ===============================
# Hapus data lama (opsional)
# ===============================
cursor.execute("DELETE FROM production_data")
conn.commit()

# ===============================
# Import data
# ===============================
sql = """
INSERT INTO production_data
(component_type,
 solder_quality,
 aoi_result,
 reflow_temp,
 conveyor_speed,
 placement_accuracy,
 spi_result,
 label)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
"""

for _, row in df.iterrows():

    data = (
        row["Component_Type"],
        row["Solder_Quality"],
        row["AOI_Result"],
        int(row["Reflow_Temp"]),
        float(row["Conveyor_Speed"]),
        float(row["Placement_Accuracy"]),
        row["SPI_Result"],
        row["Label"]
    )

    cursor.execute(sql, data)

conn.commit()

print("===================================")
print("IMPORT DATA BERHASIL")
print("Jumlah Data :", len(df))
print("===================================")

cursor.close()
conn.close()