import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",      # ganti sesuai password Anda
        database="smt_production"
    )

    print("Koneksi Berhasil")

except Exception as e:
    print(e)