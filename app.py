from flask import Flask, render_template, request, redirect, session, send_from_directory, url_for, flash, send_file
from modules.upload import upload_dataset
from database.mongodb import users_collection,reports_collection
from werkzeug.security import generate_password_hash, check_password_hash
from database.mongodb import datasets_collection
from datetime import datetime
from modules.cleaning import get_dataset_info, clean_dataset
from modules.eda import dataset_info,statistical_summary,missing_report,generate_ai_insights,correlation_heatmap,generate_histograms
import pandas as pd
import os
import re
import time
from modules.visualization import load_dataset,get_columns,create_chart
from modules.ml import load_dataset,dataset_summary,get_target_columns,detect_problem,recommended_models,train_ml_model, get_prediction_fields, predict_future
import joblib
from modules.ai import (
    generate_complete_insight,
    dataset_chat,
    explain_prediction,
    explain_ml_result,
    explain_feature_importance
)
from modules.report import create_pdf_report
from bson import ObjectId
from flask import abort

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

from config import *

app.secret_key = SECRET_KEY


# HOME

@app.route("/")
def home():
    return render_template("index.html")


# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user["password"], password):

            session["user_name"] = user["name"]
            session["email"] = user["email"]

            return redirect("/dashboard")

        else:
            message = "Invalid Email or Password!"

    return render_template("login.html", message=message)


# UPLOAD 
@app.route("/upload", methods=["GET", "POST"])
def upload():

    summary = None

    if "user_name" not in session:
        return redirect("/login")

    if request.method == "POST":

        file = request.files.get("file")

        if file:

            summary = upload_dataset(file)

            session["dataset_path"] = summary["filepath"]

            datasets_collection.insert_one({

                "user_email": session.get("email"),

                "file_name": summary["file_name"],

                "original_name": summary["original_name"],

                "rows": summary["rows"],

                "columns": summary["columns"],

                "uploaded_at": datetime.now()

            })

    return render_template(

        "upload.html",

        user_name=session["user_name"],

        summary=summary

    )

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""
    success = ""

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Passwords do not match
        if password != confirm_password:

            message = "Passwords do not match!"

            return render_template(
                "register.html",
                message=message,
                success=success
            )

        # Check existing email
        existing_user = users_collection.find_one(
            {"email": email}
        )

        if existing_user:

            message = "Email already registered!"

            return render_template(
                "register.html",
                message=message,
                success=success
            )

        # Encrypt password
        hashed_password = generate_password_hash(password)

        # Store user
        users_collection.insert_one({

            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now()

        })

        success = "Account created successfully! Please login."

        return render_template(
            "register.html",
            success=success,
            message=message
        )

    return render_template(
        "register.html",
        message=message,
        success=success
    )

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    message = ""
    success = ""
    email_verified = False
    email = ""

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        # Step 1 : Verify Email
        if "verify_email" in request.form:

            user = users_collection.find_one({"email": email})

            if user:
                email_verified = True
            else:
                message = "Email is not registered."

        # Step 2 : Update Password
        elif "update_password" in request.form:

            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            user = users_collection.find_one({"email": email})

            if not user:

                message = "Email is not registered."

            elif password != confirm_password:

                message = "Passwords do not match."
                email_verified = True

            else:

                hashed_password = generate_password_hash(password)

                users_collection.update_one(
                    {"email": email},
                    {
                        "$set":
                        {
                            "password": hashed_password
                        }
                    }
                )

                success = "Password updated successfully!"

                return render_template(
                    "forgot_password.html",
                    success=success
                )

    return render_template(
        "forgot_password.html",
        message=message,
        success=success,
        email_verified=email_verified,
        email=email
    )

@app.route("/dashboard")
def dashboard():

    user_name = session.get("user_name")
    user_email = session.get("email")

    datasets = list(

        datasets_collection.find(

            {"user_email": user_email}

        ).sort("uploaded_at", -1).limit(5)

    )

    reports = list(

        reports_collection.find(

            {"user_email": user_email}

        ).sort("created_at", -1).limit(5)

    )

    dataset_count = datasets_collection.count_documents(

        {"user_email": user_email}

    )

    report_count = reports_collection.count_documents(

        {"user_email": user_email}

    )

    return render_template(

        "dashboard.html",

        user_name=user_name,

        dataset_count=dataset_count,

        report_count=report_count,

        datasets=datasets,

        reports=reports

    )

@app.route("/profile")
def profile():

    user_email = session.get("email")

    dataset_count = datasets_collection.count_documents({
        "user_email": user_email
    })

    report_count = reports_collection.count_documents({
        "user_email": user_email
    })

    user = users_collection.find_one({
        "email": user_email
    })

    return render_template(

        "profile.html",

        user_name=user["name"],

        email=user["email"],

        dataset_count=dataset_count,

        report_count=report_count,

        joined_date=user.get("created_at")

    )

@app.route("/upload_history")
def upload_history():

    user_email = session.get("email")

    datasets = list(

        datasets_collection.find(

            {

                "user_email": user_email

            }

        ).sort(

            "uploaded_at",

            -1

        )

    )

    return render_template(

        "upload_history.html",

        user_name=session.get("user_name"),

        datasets=datasets

    )


@app.route("/reports")
def reports():

    user_email = session.get("email")

    reports = list(

        reports_collection.find(

            {

                "user_email": user_email

            }

        ).sort(

            "created_at",

            -1

        )

    )

    return render_template(

        "reports.html",

        user_name=session.get("user_name"),

        reports=reports

    )

# ================= VIEW REPORT =================

@app.route("/view_report/<report_id>")
def view_report(report_id):

    report = reports_collection.find_one(
        {
            "_id": ObjectId(report_id)
        }
    )

    if report is None:

        abort(404)

    return send_file(
        report["report_path"],
        mimetype="application/pdf"
    )


# ================= DOWNLOAD REPORT =================

@app.route("/download_report/<report_id>")
def download_report(report_id):

    report = reports_collection.find_one(
        {
            "_id": ObjectId(report_id)
        }
    )

    if report is None:

        abort(404)

    return send_file(

        report["report_path"],

        as_attachment=True,

        download_name=report["report_name"]

    )


# ================= DELETE REPORT =================

@app.route("/delete_report/<report_id>")
def delete_report(report_id):

    report = reports_collection.find_one(
        {
            "_id": ObjectId(report_id)
        }
    )

    if report:

        if os.path.exists(report["report_path"]):

            os.remove(report["report_path"])

        reports_collection.delete_one(
            {
                "_id": ObjectId(report_id)
            }
        )

    return redirect("/reports")

@app.route("/cleaning", methods=["GET", "POST"])
def cleaning():

    if "dataset_path" not in session:
        return redirect("/upload")

    filepath = session["dataset_path"]

    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath, low_memory=False)
    else:
        df = pd.read_excel(filepath)

    summary = {

        "rows": len(df),

        "columns": len(df.columns),

        "missing": int(df.isnull().sum().sum()),

        "duplicates": int(df.duplicated().sum())

    }

    report = None

    if request.method == "POST":

        start = time.time()

        original_rows = len(df)

        original_missing = int(df.isnull().sum().sum())

        original_duplicates = int(df.duplicated().sum())

        # -------------------------
        # Remove Missing Values
        # -------------------------

        if request.form.get("remove_missing"):

            df.dropna(inplace=True)

        # -------------------------
        # Fill Mean
        # -------------------------

        if request.form.get("fill_mean"):

            numeric = df.select_dtypes(include="number").columns

            for col in numeric:

                df[col] = df[col].fillna(df[col].mean())

        # -------------------------
        # Fill Median
        # -------------------------

        if request.form.get("fill_median"):

            numeric = df.select_dtypes(include="number").columns

            for col in numeric:

                df[col] = df[col].fillna(df[col].median())

        # -------------------------
        # Fill Mode
        # -------------------------

        if request.form.get("fill_mode"):

            for col in df.columns:

                mode = df[col].mode()

                if not mode.empty:

                    df[col] = df[col].fillna(mode[0])

        # -------------------------
        # Remove Duplicate Rows
        # -------------------------

        if request.form.get("remove_duplicates"):

            df.drop_duplicates(inplace=True)

        # -------------------------
        # Standardize Column Names
        # -------------------------

        if request.form.get("standardize_columns"):

            df.columns = [

                col.strip().lower().replace(" ", "_")

                for col in df.columns

            ]

        # -------------------------
        # Remove Empty Columns
        # -------------------------

        if request.form.get("remove_empty_columns"):

            df.dropna(axis=1, how="all", inplace=True)

        # -------------------------
        # Remove Constant Columns
        # -------------------------

        if request.form.get("remove_constant_columns"):

            constant = [

                c for c in df.columns

                if df[c].nunique() <= 1

            ]

            df.drop(columns=constant, inplace=True)

        # -------------------------
        # Trim Spaces
        # -------------------------

        if request.form.get("trim_spaces"):

            text = df.select_dtypes(include="object").columns

            for col in text:

                df[col] = df[col].astype(str).str.strip()

        # -------------------------
        # Remove Special Characters
        # -------------------------

        if request.form.get("remove_special"):

            text = df.select_dtypes(include="object").columns

            for col in text:

                df[col] = df[col].str.replace(

                    r'[^A-Za-z0-9 ]',

                    '',

                    regex=True

                )

        # -------------------------
        # Title Case
        # -------------------------

        if request.form.get("standardize_text"):

            text = df.select_dtypes(include="object").columns

            for col in text:

                df[col] = df[col].str.title()

        # -------------------------
        # Convert Datatypes
        # -------------------------

        if request.form.get("convert_types"):

            df = df.convert_dtypes()

        # -------------------------
        # Save Cleaned Dataset
        # -------------------------

        cleaned_folder = "cleaned"

        os.makedirs(cleaned_folder, exist_ok=True)

        cleaned_file = os.path.join(

            cleaned_folder,

            "cleaned_dataset.csv"

        )

        df.to_csv(

            cleaned_file,

            index=False

        )

        session["cleaned_dataset"] = cleaned_file

        report = {

            "rows_removed":

                original_rows - len(df),

            "missing_fixed":

                original_missing -

                int(df.isnull().sum().sum()),

            "duplicates_removed":

                original_duplicates -

                int(df.duplicated().sum()),

            "processing_time":

                round(

                    time.time()-start,

                    2

                ),

            "cleaned_filename":

                "cleaned_dataset.csv"

        }

    return render_template(
    "cleaning.html",
    summary=summary,
    report=report,
    user_name=session["user_name"]
)

@app.route("/download_cleaned/<filename>")
def download_cleaned(filename):

    path = os.path.join(

        "cleaned",

        filename

    )

    return send_file(

        path,

        as_attachment=True

    )

@app.route("/eda")
def eda():

    if "cleaned_dataset" in session:

        filepath = session["cleaned_dataset"]

    elif "dataset_path" in session:

        filepath = session["dataset_path"]

    else:

        return redirect("/upload")

    if filepath.endswith(".csv"):

        df = pd.read_csv(filepath, low_memory=False)

    else:

        df = pd.read_excel(filepath)

    info = dataset_info(df)

    stats_table = statistical_summary(df)

    missing_table = missing_report(df)

    insights = generate_ai_insights(df)
    heatmap=correlation_heatmap(df)
    histograms=generate_histograms(df)

    return render_template(
    "eda.html",
    user_name=session.get("user_name","User"),
    info=info,
    stats_table=stats_table,
    missing_table=missing_table,
    insights=insights,
    heatmap=heatmap,
    histograms=histograms
    )

@app.route("/visualization",methods=["GET","POST"])
def visualization():

    if "cleaned_dataset" in session:
        filepath=session["cleaned_dataset"]
    elif "dataset_path" in session:
        filepath=session["dataset_path"]
    else:
        return redirect("/upload")

    df=load_dataset(filepath)

    numeric,categorical=get_columns(df)

    all_columns=df.columns.tolist()

    chart=None

    if request.method=="POST":

        chart_type=request.form["chart"]

        x_column=request.form["x_column"]

        y_column=request.form.get("y_column")

        if y_column=="":
            y_column=None

        chart=create_chart(
            df,
            chart_type,
            x_column,
            y_column
        )

    return render_template(
        "visualization.html",
        user_name=session.get("user_name","User"),
        numeric=numeric,
        categorical=categorical,
        all_columns=all_columns,
        chart=chart
    )

@app.route("/ml",methods=["GET","POST"])
def ml():

    if "cleaned_dataset" in session:

        filepath=session["cleaned_dataset"]

    elif "dataset_path" in session:

        filepath=session["dataset_path"]

    else:

        return redirect("/upload")

    df=load_dataset(filepath)

    summary=dataset_summary(df)

    columns=get_target_columns(df)

    selected_target=None

    problem=None

    models=[]

    if request.method=="POST":

        selected_target=request.form["target"]

        problem=detect_problem(df,selected_target)

        models=recommended_models(problem)

    return render_template(

        "ml.html",

        user_name=session.get("user_name","User"),

        summary=summary,

        columns=columns,

        selected_target=selected_target,

        problem=problem,

        models=models

    )

@app.route("/train_model",methods=["POST"])
def train_model():

    if "cleaned_dataset" in session:

        filepath=session["cleaned_dataset"]

    elif "dataset_path" in session:

        filepath=session["dataset_path"]

    else:

        return redirect("/upload")

    df=load_dataset(filepath)

    summary=dataset_summary(df)

    columns=get_target_columns(df)

    target=request.form["target"]

    model=request.form["model"]

    problem=detect_problem(df,target)

    models=recommended_models(problem)

    
    result = train_ml_model(df, target, model)

    ai_result = generate_complete_insight(filepath, result)

    session["ai_story"] = ai_result["story"]

    session["dataset_summary"] = ai_result["summary"]

    session["model_path"]=result["model_path"]

    session["metadata_path"]=result["metadata_path"]
    
    session["ml_result"]=result
    session["ml_target"]=target
    session["ml_model"]=model
    session["ml_problem"]=problem


    if result["problem"]=="Classification":

        ai_message=f"""
The selected model '{model}' achieved an accuracy of {result['accuracy']}%.

This indicates that the model performs well in classifying the selected target variable.

You may compare this model with other recommended algorithms to identify the best-performing model for your dataset.
"""

    else:

        ai_message=f"""
The selected model '{model}' achieved an R² Score of {result['r2']}.

A higher R² score indicates that the model explains a larger proportion of the variance in the target variable.

You can also compare this model with other regression algorithms for improved performance.
"""

    session["ml_ai_message"]=ai_message
    return render_template(

        "ml_result.html",

        user_name=session.get("user_name","User"),

        summary=summary,

        target=target,

        model=model,

        problem=problem,

        models=models,

        result=result,

        ai_message=ai_message

    )

@app.route("/ml_result")
def ml_result():

    if "ml_result" not in session:

        return redirect("/ml")

    return render_template(

        "ml_result.html",

        user_name=session.get("user_name","User"),

        result=session["ml_result"],

        target=session["ml_target"],

        model=session["ml_model"],

        problem=session["ml_problem"],

        ai_message=session["ml_ai_message"]

    )

@app.route("/download_model")
def download_model():

    if not os.path.exists("trained_models"):

        return "No trained model found."

    files=os.listdir("trained_models")

    if len(files)==0:

        return "No trained model found."

    model_path=os.path.join("trained_models",files[-1])

    return send_file(

        model_path,

        as_attachment=True

    )

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    if "cleaned_dataset" in session:

        filepath = session["cleaned_dataset"]

    elif "dataset_path" in session:

        filepath = session["dataset_path"]

    else:

        return redirect("/upload")


    # Load trained model and metadata
    loaded_model = joblib.load(session["model_path"])

    metadata = joblib.load(session["metadata_path"])


    target = request.args.get("target")

    model_name = request.args.get("model")


    if target is None or model_name is None:

        return redirect("/ml")


    metadata_path = f"trained_models/{model_name}_metadata.joblib"

    model_path = f"trained_models/{model_name}.joblib"


    fields = get_prediction_fields(metadata_path)


    prediction = None


    if request.method == "POST":

        input_data = {}

        for field in fields:

            input_data[field] = request.form[field]

        prediction = predict_future(

            model_path,

            metadata_path,

            input_data

        )
        session["prediction_count"] = session.get("prediction_count", 0) + 1
    session["prediction"] = prediction


    return render_template(

        "prediction.html",

        user_name=session.get("user_name", "User"),

        fields=fields,

        prediction=prediction,

        target=target,

        model=model_name

    )

@app.route("/ai_story")
def ai_story():

    try:

        if "dataset_path" not in session:

            return redirect("/upload")


        filepath = session["dataset_path"]

        ml_result = session.get("ml_result")


        # Generate only if not already available

        if "ai_story" not in session:


            result = generate_complete_insight(

                filepath,

                ml_result

            )


            session["ai_story"] = result["story"]

            session["dataset_summary"] = result["summary"]



        return render_template(

            "ai_insights.html",

            user_name=session.get("user_name","User"),

            story=session.get("ai_story",""),

            summary=session.get("dataset_summary",{}),

            ml_result=session.get("ml_result",{})

        )


    except Exception as e:


        return render_template(

            "ai_insights.html",

            user_name=session.get("user_name","User"),

            story=f"AI Story Generation Failed.\n\nReason:\n{str(e)}",

            summary={

                "Rows":0,

                "Columns":0,

                "Numeric Columns":0,

                "Categorical Columns":0,

                "Missing Values":0,

                "Duplicate Rows":0

            },

            ml_result={}

        )
    
@app.route("/dataset_chat", methods=["POST"])
def dataset_chat_route():

    if "cleaned_dataset" in session:

        filepath = session["cleaned_dataset"]

    elif "dataset_path" in session:

        filepath = session["dataset_path"]

    else:

        return redirect("/upload")

    df = load_dataset(filepath)

    question = request.form["question"]

    answer = dataset_chat(question, df)

    return {

        "answer": answer

    }

@app.route("/report")
def report():

    if "dataset_path" not in session and "cleaned_dataset" not in session:

        return redirect("/upload")

    filepath = session.get("cleaned_dataset") or session.get("dataset_path")

    dataset_summary = session.get("dataset_summary", {})

    ml_result = session.get("ml_result", {})

    ai_story = session.get("ai_story", "")

    prediction = session.get("prediction")

    chart_path = ml_result.get("chart") if ml_result else None

    os.makedirs("static/reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_name = f"DataInsight_AI_Report_{timestamp}.pdf"

    pdf_path = os.path.join(

        "static",

        "reports",

        report_name

    )

    create_pdf_report(

        pdf_path=pdf_path,

        dataset_summary=dataset_summary,

        ml_result=ml_result,

        ai_story=ai_story,

        chart_path=chart_path,

        prediction=prediction

    )

    reports_collection.insert_one({

        "user_email": session.get("email"),

        "user_name": session.get("user_name"),

        "dataset_name": os.path.basename(filepath),

        "report_name": report_name,

        "report_path": pdf_path.replace("\\", "/"),

        "problem_type": ml_result.get("problem", ""),

        "model": session.get("ml_model", ""),

        "created_at": datetime.now()

    })

    return render_template(

        "report.html",

        user_name=session.get("user_name"),

        dataset_summary=dataset_summary,

        ml_result=ml_result,

        ai_story=ai_story,

        prediction=prediction,

        pdf_path=pdf_path,

        pdf_file=report_name

    )

@app.route("/download_latest_report")
def download_latest_report():

    reports = reports_collection.find_one(

    {"user_email": session.get("email")},

    sort=[("created_at", -1)]

)

    if reports is None:

        return redirect("/report")

    return send_file(

        reports["report_path"],

        as_attachment=True

    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)