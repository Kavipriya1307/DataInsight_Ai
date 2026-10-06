import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,r2_score,mean_absolute_error,mean_squared_error,confusion_matrix
from sklearn.linear_model import LinearRegression,LogisticRegression
from sklearn.tree import DecisionTreeClassifier,DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor,GradientBoostingRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

def load_dataset(filepath):

    if filepath.endswith(".csv"):

        df=pd.read_csv(filepath,low_memory=False)

    else:

        df=pd.read_excel(filepath)

    return df

def dataset_summary(df):

    numeric=df.select_dtypes(include=["number"]).columns.tolist()

    categorical=df.select_dtypes(exclude=["number"]).columns.tolist()

    return{

        "rows":df.shape[0],

        "columns":df.shape[1],

        "numeric":len(numeric),

        "categorical":len(categorical),

        "missing":int(df.isnull().sum().sum())

    }

def get_target_columns(df):

    return df.columns.tolist()

def detect_problem(df,target):

    if df[target].dtype=="object":

        return "Classification"

    if df[target].nunique()<=10:

        return "Classification"

    return "Regression"

def recommended_models(problem):

    if problem=="Classification":

        return[
            "Logistic Regression",
            "Decision Tree",
            "Random Forest",
            "Support Vector Machine",
            "K-Nearest Neighbors"
        ]

    return[
        "Linear Regression",
        "Decision Tree Regressor",
        "Random Forest Regressor",
        "Gradient Boosting Regressor"
    ]

def preprocess_dataset(df,target):

    df=df.copy()

    encoders={}

    for col in df.columns:

        if col!=target and df[col].dtype=="object":

            encoder=LabelEncoder()

            df[col]=encoder.fit_transform(df[col].astype(str))

            encoders[col]=encoder

    target_encoder=None

    if df[target].dtype=="object":

        target_encoder=LabelEncoder()

        df[target]=target_encoder.fit_transform(df[target].astype(str))

    X=df.drop(columns=[target])

    y=df[target]

    return X,y,encoders,target_encoder

def train_ml_model(df,target,model_name):

    problem=detect_problem(df,target)

    X,y,encoders,target_encoder=preprocess_dataset(df,target)

    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)

    if problem=="Classification":

        if model_name=="Logistic Regression":

            model=LogisticRegression(max_iter=1000)

        elif model_name=="Decision Tree":

            model=DecisionTreeClassifier(random_state=42)

        elif model_name=="Random Forest":

            model=RandomForestClassifier(random_state=42)

        elif model_name=="Support Vector Machine":

            model=SVC(probability=True)

        else:

            model=KNeighborsClassifier()

    else:

        if model_name=="Linear Regression":

            model=LinearRegression()

        elif model_name=="Decision Tree Regressor":

            model=DecisionTreeRegressor(random_state=42)

        elif model_name=="Random Forest Regressor":

            model=RandomForestRegressor(random_state=42)

        else:

            model=GradientBoostingRegressor(random_state=42)

    model.fit(X_train,y_train)

    predictions=model.predict(X_test)

    os.makedirs("trained_models",exist_ok=True)

    model_path=f"trained_models/{model_name}.joblib"

    metadata_path=f"trained_models/{model_name}_metadata.joblib"

    joblib.dump(model,model_path)

    joblib.dump({

        "columns":X.columns.tolist(),

        "encoders":encoders,

        "target_encoder":target_encoder

    },metadata_path)

    feature_importance=None

    if hasattr(model,"feature_importances_"):

        feature_importance=dict(zip(X.columns,model.feature_importances_))

        feature_importance=dict(sorted(feature_importance.items(),key=lambda x:x[1],reverse=True))

    os.makedirs("static/charts",exist_ok=True)

    if problem=="Classification":

        cm=confusion_matrix(y_test,predictions)

        plt.figure(figsize=(6,5))

        sns.heatmap(cm,annot=True,fmt="d",cmap="Blues")

        plt.title("Confusion Matrix")

        plt.xlabel("Predicted")

        plt.ylabel("Actual")

        chart_path="static/charts/confusion_matrix.png"

        plt.savefig(chart_path,bbox_inches="tight")

        plt.close()

        accuracy=accuracy_score(y_test,predictions)

        precision=precision_score(y_test,predictions,average="weighted",zero_division=0)

        recall=recall_score(y_test,predictions,average="weighted",zero_division=0)

        f1=f1_score(y_test,predictions,average="weighted",zero_division=0)

        return{

            "problem":"Classification",

            "accuracy":round(accuracy*100,2),

            "precision":round(precision*100,2),

            "recall":round(recall*100,2),

            "f1":round(f1*100,2),

            "train_samples":len(X_train),

            "test_samples":len(X_test),

            "feature_importance":feature_importance,

            "chart":chart_path,

            "model_path":model_path,

            "metadata_path":metadata_path,

            "predictions":predictions.tolist(),

            "actual":y_test.tolist()

        }

    else:

        plt.figure(figsize=(6,5))

        plt.scatter(y_test,predictions,color="royalblue")

        plt.plot([y_test.min(),y_test.max()],

                 [y_test.min(),y_test.max()],

                 "r--")

        plt.xlabel("Actual Values")

        plt.ylabel("Predicted Values")

        plt.title("Actual vs Predicted")

        chart_path="static/charts/regression_plot.png"

        plt.savefig(chart_path,bbox_inches="tight")

        plt.close()

        r2=r2_score(y_test,predictions)

        mae=mean_absolute_error(y_test,predictions)

        rmse=np.sqrt(mean_squared_error(y_test,predictions))

        return{

            "problem":"Regression",

            "r2":round(r2,3),

            "mae":round(mae,3),

            "rmse":round(rmse,3),

            "train_samples":len(X_train),

            "test_samples":len(X_test),

            "feature_importance":feature_importance,

            "chart":chart_path,

            "model_path":model_path,

            "metadata_path":metadata_path,

            "predictions":predictions.tolist(),

            "actual":y_test.tolist()

        }
    
def get_prediction_fields(metadata_path):

    metadata=joblib.load(metadata_path)

    return metadata["columns"]

def predict_future(model_path,metadata_path,input_data):

    model=joblib.load(model_path)

    metadata=joblib.load(metadata_path)

    columns=metadata["columns"]

    encoders=metadata["encoders"]

    target_encoder=metadata["target_encoder"]

    values=[]

    for col in columns:

        value=input_data[col]

        if col in encoders:

            encoder=encoders[col]

            if value not in encoder.classes_:

                raise ValueError(f"{value} is not present in training data.")

            value=encoder.transform([value])[0]

        else:

            value=float(value)

        values.append(value)

    prediction=model.predict([values])[0]

    if target_encoder is not None:

        prediction=target_encoder.inverse_transform([int(prediction)])[0]

    return prediction