from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, session, flash
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for
)

import pandas as pd
import mysql.connector
import joblib
import numpy as np

db=mysql.connector.connect(
    host="HOST_RAILWAY",
    user="USERNAME",
    password="PASSWORD",
    database="railway",
    port=6543
)

cursor = db.cursor(buffered=True)

app = Flask(__name__)
app.secret_key = "smt_production_2026"


@app.route("/")
def home():

    if "login" in session:
        return redirect("/dashboard")

    return redirect("/login")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    sql = """
    SELECT *
    FROM admin
    WHERE username=%s
    AND password=%s
    """

    cursor.execute(sql,(username,password))

    admin = cursor.fetchone()

    if admin:

        session["login"] = True
        session["username"] = admin[1]
        session["nama"] = admin[3]

        return redirect("/dashboard")

    flash("Username atau Password salah!", "danger")

    return redirect("/login")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/dashboard")
def dashboard():

    if "login" not in session:
        return redirect("/login")

    cursor.execute("SELECT COUNT(*) FROM production_data")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM production_data WHERE label='Good'")
    good = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM production_data WHERE label='Defect'")
    defect = cursor.fetchone()[0]

    akurasi = 96.8

    cursor.execute("""
        SELECT component_type, COUNT(*)
        FROM production_data
        GROUP BY component_type
    """)

    component = cursor.fetchall()

    component_label = []
    component_total = []

    for row in component:
        component_label.append(row[0])
        component_total.append(row[1])

    return render_template(
    "dashboard.html",
    total=total,
    good=good,
    defect=defect,
    accuracy=akurasi,
    component_label=component_label,
    component_total=component_total
)

model = joblib.load("model/model.pkl")
encoder = joblib.load("model/encoder.pkl")

@app.route("/chart")
def chart():

    cursor.execute("""
        SELECT prediction,
               COUNT(*)
        FROM prediction_history
        GROUP BY prediction
    """)

    result = cursor.fetchall()

    labels = []
    values = []

    for row in result:
        labels.append(row[0])
        values.append(row[1])

    return render_template(
        "chart.html",
        labels=labels,
        values=values
    )

# ===============================
# ROUTE HISTORY
# ===============================
@app.route("/history")
def history():

    if "login" not in session:
        return redirect("/login")

    cursor.execute("""
        SELECT
            id,
            component_type,
            solder_quality,
            aoi_result,
            reflow_temp,
            conveyor_speed,
            placement_accuracy,
            spi_result,
            prediction,
            prediction_time
        FROM prediction_history
        ORDER BY prediction_time DESC
    """)

    data = cursor.fetchall()

    return render_template(
        "history.html",
        data=data
    )

@app.route("/add_production", methods=["GET","POST"])
def add_production():

    if request.method == "POST":

        component=request.form["component_type"]
        solder=request.form["solder_quality"]
        aoi=request.form["aoi_result"]
        temp=request.form["reflow_temp"]
        speed=request.form["conveyor_speed"]
        placement=request.form["placement_accuracy"]
        spi=request.form["spi_result"]
        label=request.form["label"]

        sql="""
        INSERT INTO production_data
        (
            component_type,
            solder_quality,
            aoi_result,
            reflow_temp,
            conveyor_speed,
            placement_accuracy,
            spi_result,
            label
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(sql,(
            component,
            solder,
            aoi,
            temp,
            speed,
            placement,
            spi,
            label
        ))

        db.commit()

        return redirect("/production")

    return render_template("add_production.html")

@app.route("/production")
def production():

    if "login" not in session:
        return redirect("/login")

    keyword = request.args.get("keyword")

    if keyword:

        cursor.execute("""
            SELECT
                id,
                component_type,
                solder_quality,
                aoi_result,
                reflow_temp,
                conveyor_speed,
                placement_accuracy,
                spi_result,
                label
            FROM production_data
            WHERE component_type LIKE %s
            ORDER BY id ASC
        """, ("%" + keyword + "%",))

    else:

        cursor.execute("""
            SELECT
                id,
                component_type,
                solder_quality,
                aoi_result,
                reflow_temp,
                conveyor_speed,
                placement_accuracy,
                spi_result,
                label
            FROM production_data
            ORDER BY id ASC
        """)

    data = cursor.fetchall()

    return render_template(
        "production.html",
        data=data
    )

@app.route("/delete_production/<int:id>")
def delete_production(id):

    cursor.execute(
        "DELETE FROM production_data WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect("/production")

@app.route("/edit_production/<int:id>", methods=["GET","POST"])
def edit_production(id):

    if request.method=="POST":

        component=request.form["component_type"]

        solder=request.form["solder_quality"]

        aoi=request.form["aoi_result"]

        temp=request.form["reflow_temp"]

        speed=request.form["conveyor_speed"]

        placement=request.form["placement_accuracy"]

        spi=request.form["spi_result"]

        label=request.form["label"]

        sql="""
        UPDATE production_data

        SET

        component_type=%s,

        solder_quality=%s,

        aoi_result=%s,

        reflow_temp=%s,

        conveyor_speed=%s,

        placement_accuracy=%s,

        spi_result=%s,

        label=%s

        WHERE id=%s
        """

        cursor.execute(sql,(
            component,
            solder,
            aoi,
            temp,
            speed,
            placement,
            spi,
            label,
            id
        ))

        db.commit()

        return redirect("/production")

    cursor.execute(
        "SELECT * FROM production_data WHERE id=%s",
        (id,)
    )

    data=cursor.fetchone()

    return render_template(
        "edit_production.html",
        data=data
    )

@app.route("/prediction")
def prediction():

    if "login" not in session:
        return redirect("/login")

    return render_template("predict.html")

@app.route("/predict", methods=["POST"])
def predict():

    # ===============================
    # Ambil Data dari Form
    # ===============================
    component = request.form["component_type"]
    solder = request.form["solder_quality"]
    aoi = request.form["aoi_result"]
    temp = request.form["reflow_temp"]
    speed = request.form["conveyor_speed"]
    placement = request.form["placement_accuracy"]
    spi = request.form["spi_result"]

    # ===============================
    # Validasi Input Kosong
    # ===============================
    if component == "":
        return "Component Type harus dipilih."

    if solder == "":
        return "Solder Quality harus dipilih."

    if aoi == "":
        return "AOI Result harus dipilih."

    if spi == "":
        return "SPI Result harus dipilih."

    # ===============================
    # Ubah ke Float
    # ===============================
    temp = float(temp)
    speed = float(speed)
    placement = float(placement)

    # ===============================
    # Validasi Nilai
    # ===============================
    if temp < 200 or temp > 260:
        return "Reflow Temperature harus antara 200–260°C."

    if speed < 0.5 or speed > 2.5:
        return "Conveyor Speed harus antara 0.5–2.5 m/min."

    if placement < 80 or placement > 100:
        return "Placement Accuracy harus antara 80–100%."

    # ===============================
    # Encode Data
    # ===============================
    component_encode = encoder["component_type"].transform([component])[0]
    solder_encode = encoder["solder_quality"].transform([solder])[0]
    aoi_encode = encoder["aoi_result"].transform([aoi])[0]
    spi_encode = encoder["spi_result"].transform([spi])[0]

    # ===============================
    # Data untuk Prediksi
    # ===============================
    data = np.array([[
        component_encode,
        solder_encode,
        aoi_encode,
        temp,
        speed,
        placement,
        spi_encode
    ]])

    # ===============================
    # Prediksi
    # ===============================
    hasil = model.predict(data)

    if hasil[0] == 1:
        prediksi = "Good"
    else:
        prediksi = "Defect"

    # ===============================
    # Simpan ke Database
    # ===============================
    sql = """
    INSERT INTO prediction_history
    (
        component_type,
        solder_quality,
        aoi_result,
        reflow_temp,
        conveyor_speed,
        placement_accuracy,
        spi_result,
        prediction
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    data_db = (
        component,
        solder,
        aoi,
        temp,
        speed,
        placement,
        spi,
        prediksi
    )

    cursor.execute(sql, data_db)
    db.commit()

    return render_template(
        "result.html",
        hasil=prediksi
    )

from flask import send_file
import pandas as pd

@app.route("/export_excel")
def export_excel():

    query = """
    SELECT *
    FROM prediction_history
    ORDER BY prediction_time DESC
    """

    df = pd.read_sql(query, db)

    file_name = "Riwayat_Prediksi.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(file_name, as_attachment=True)

@app.route("/export_pdf")
def export_pdf():

    cursor.execute("""
        SELECT
            id,
            component_type,
            solder_quality,
            aoi_result,
            reflow_temp,
            conveyor_speed,
            placement_accuracy,
            spi_result,
            label
        FROM production_data
    """)

    data = cursor.fetchall()

    file_name = "Laporan_Data_Produksi.pdf"

    pdf = SimpleDocTemplate(file_name)

    table_data = [[
        "ID",
        "Component",
        "Solder",
        "AOI",
        "Temp",
        "Speed",
        "Placement",
        "SPI",
        "Label"
    ]]

    for row in data:
        table_data.append(list(row))

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
    ]))

    pdf.build([table])

    return send_file(file_name, as_attachment=True)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.model_selection import train_test_split

@app.route("/evaluation")
def evaluation():

    query = """
    SELECT
        component_type,
        solder_quality,
        aoi_result,
        reflow_temp,
        conveyor_speed,
        placement_accuracy,
        spi_result,
        label
    FROM production_data
    """

    df = pd.read_sql(query, db)

    encoder = joblib.load("model/encoder.pkl")

    df["component_type"] = encoder["component_type"].transform(df["component_type"])
    df["solder_quality"] = encoder["solder_quality"].transform(df["solder_quality"])
    df["aoi_result"] = encoder["aoi_result"].transform(df["aoi_result"])
    df["spi_result"] = encoder["spi_result"].transform(df["spi_result"])

    df["label"] = df["label"].map({
        "Good": 1,
        "Defect": 0
    })

    X = df.drop("label", axis=1)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = joblib.load("model/model.pkl")

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    return render_template(
    "evaluation.html",
    accuracy=round(accuracy*100, 2),
    precision=round(precision*100, 2),
    recall=round(recall*100, 2),
    f1=round(f1*100, 2),
    confusion_image="confusion_matrix.png"
)

@app.route("/feature_importance")
def feature_importance():

    model = joblib.load("model/model.pkl")

    feature_names = [
        "Component Type",
        "Solder Quality",
        "AOI Result",
        "Reflow Temperature",
        "Conveyor Speed",
        "Placement Accuracy",
        "SPI Result"
    ]

    importance = model.feature_importances_

    data = list(zip(feature_names, importance))

    data = sorted(data, key=lambda x: x[1], reverse=True)

    return render_template(
        "feature_importance.html",
        data=data
    )

@app.route("/decision_tree")
def decision_tree():

    model = joblib.load("model/model.pkl")

    feature_names = [
        "Component Type",
        "Solder Quality",
        "AOI Result",
        "Reflow Temperature",
        "Conveyor Speed",
        "Placement Accuracy",
        "SPI Result"
    ]

    class_names = ["Defect", "Good"]

    plt.figure(figsize=(20,10))

    plot_tree(
        model,
        feature_names=feature_names,
        class_names=class_names,
        filled=True,
        rounded=True,
        fontsize=8
    )

    plt.savefig("static/decision_tree.png")
    plt.close()

    return render_template("decision_tree.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/profile")
def profile():

    if "username" not in session:
        return redirect("/login")

    return render_template(
        "profile.html",
        username=session["username"]
    )

@app.route("/model_information")
def model_information():

    model = joblib.load("model/model.pkl")

    return render_template(
        "model_information.html",
        depth=model.get_depth(),
        leaves=model.get_n_leaves()
    )

@app.route("/statistics")
def statistics():

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM production_data")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM production_data WHERE label='Good'")
    good = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM production_data WHERE label='Defect'")
    defect = cursor.fetchone()[0]

    cursor.execute("""
        SELECT component_type, COUNT(*)
        FROM production_data
        GROUP BY component_type
    """)

    component = cursor.fetchall()

    component_label = []
    component_total = []

    for row in component:
        component_label.append(row[0])
        component_total.append(row[1])

    cursor.close()

    return render_template(
        "statistics.html",
        total=total,
        good=good,
        defect=defect,
        component_label=component_label,
        component_total=component_total
    )

@app.route("/model_info")
def model_info():

    return render_template(
        "model_info.html",
        algorithm="Decision Tree",
        dataset="SMT Production Dataset",
        fitur=7,
        target="Good / Defect",
        accuracy="98.75%",
        precision="98.10%",
        recall="99.00%",
        f1="98.54%"
    )

if __name__ == "__main__":
    app.run(debug=True)