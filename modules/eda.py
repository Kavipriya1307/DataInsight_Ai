import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import seaborn as sns
import uuid

UPLOAD_FOLDER="uploads"

def get_latest_dataset():
    files=[os.path.join(UPLOAD_FOLDER,f) for f in os.listdir(UPLOAD_FOLDER) if f.endswith((".csv",".xlsx",".xls"))]
    if not files:
        return None
    latest=max(files,key=os.path.getctime)
    if latest.endswith(".csv"):
        df=pd.read_csv(latest)
    else:
        df=pd.read_excel(latest)
    return df,latest

def dataset_info(df):
    numeric_cols=df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols=df.select_dtypes(exclude=["number"]).columns.tolist()
    memory=round(df.memory_usage(deep=True).sum()/1024/1024,2)

    info={
        "rows":df.shape[0],
        "columns":df.shape[1],
        "numeric":len(numeric_cols),
        "categorical":len(categorical_cols),
        "memory":memory
    }

    return info

def statistical_summary(df):
    numeric=df.select_dtypes(include=["number"])

    if numeric.empty:
        return ""

    summary=pd.DataFrame({
        "Mean":numeric.mean(),
        "Median":numeric.median(),
        "Mode":numeric.mode().iloc[0],
        "Std":numeric.std(),
        "Variance":numeric.var(),
        "Minimum":numeric.min(),
        "Maximum":numeric.max(),
        "Q1":numeric.quantile(0.25),
        "Q2":numeric.quantile(0.50),
        "Q3":numeric.quantile(0.75)
    })

    summary=summary.round(2)

    return summary.to_html(classes="table",border=0)

def missing_report(df):
    report=pd.DataFrame({
        "Column":df.columns,
        "Missing Values":df.isnull().sum().values,
        "Percentage":((df.isnull().sum()/len(df))*100).round(2).values
    })

    return report.to_html(classes="table",index=False,border=0)

def generate_ai_insights(df):

    insights=[]

    total_missing=int(df.isnull().sum().sum())

    if total_missing==0:
        insights.append("No missing values found in the dataset.")
    else:
        insights.append(f"⚠ Dataset contains {total_missing} missing values.")

    duplicates=int(df.duplicated().sum())

    if duplicates==0:
        insights.append("No duplicate rows detected.")
    else:
        insights.append(f"⚠ {duplicates} duplicate rows are present.")

    numeric=df.select_dtypes(include=["number"])

    if not numeric.empty:

        highest_missing=(df.isnull().sum()/len(df)*100).idxmax()
        insights.append(f"Column '{highest_missing}' requires attention for missing values.")

        corr=numeric.corr()

        max_corr=0
        pair=None

        cols=corr.columns

        for i in range(len(cols)):
            for j in range(i+1,len(cols)):
                value=abs(corr.iloc[i,j])
                if value>max_corr:
                    max_corr=value
                    pair=(cols[i],cols[j])

        if pair:
            insights.append(f" '{pair[0]}' and '{pair[1]}' show a strong correlation ({round(max_corr,2)}).")

    insights.append("Dataset is ready for visualization and advanced analytics.")

    return insights

def correlation_heatmap(df):

    numeric=df.select_dtypes(include=["number"])

    if numeric.shape[1]<2:
        return None

    corr=numeric.corr()

    plt.figure(figsize=(10,7))

    sns.heatmap(
        corr,
        annot=True,
        cmap="Blues",
        linewidths=.5,
        fmt=".2f"
    )

    filename=f"heatmap_{uuid.uuid4().hex}.png"

    path=os.path.join("static","images",filename)

    os.makedirs("static/images",exist_ok=True)

    plt.tight_layout()

    plt.savefig(path,dpi=250)

    plt.close()

    return filename

def generate_histograms(df):

    numeric=df.select_dtypes(include=["number"])

    images=[]

    os.makedirs("static/images",exist_ok=True)

    for column in numeric.columns:

        plt.figure(figsize=(7,5))

        sns.histplot(df[column].dropna(),kde=True,color="#2563eb")

        plt.title(column)

        plt.xlabel(column)

        plt.ylabel("Frequency")

        filename=f"hist_{uuid.uuid4().hex}.png"

        path=os.path.join("static","images",filename)

        plt.tight_layout()

        plt.savefig(path,dpi=250)

        plt.close()

        images.append({
            "column":column,
            "image":filename
        })

    return images