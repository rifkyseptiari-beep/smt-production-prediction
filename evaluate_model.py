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
        accuracy=round(accuracy * 100, 2),
        precision=round(precision * 100, 2),
        recall=round(recall * 100, 2),
        f1=round(f1 * 100, 2)
    )