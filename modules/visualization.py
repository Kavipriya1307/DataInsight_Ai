import os
import pandas as pd
import plotly.express as px

def load_dataset(filepath):

    if filepath.endswith(".csv"):
        df=pd.read_csv(filepath,low_memory=False)
    else:
        df=pd.read_excel(filepath)

    return df

def get_columns(df):

    numeric=df.select_dtypes(include=["number"]).columns.tolist()

    categorical=df.select_dtypes(exclude=["number"]).columns.tolist()

    return numeric,categorical

def create_chart(df,chart,x,y):

    fig=None

    if chart=="Bar Chart":

        fig=px.bar(df,x=x,y=y,color=x)

    elif chart=="Line Chart":

        fig=px.line(df,x=x,y=y)

    elif chart=="Scatter Plot":

        fig=px.scatter(df,x=x,y=y,color=x)

    elif chart=="Box Plot":

        fig=px.box(df,x=x,y=y,color=x)

    elif chart=="Histogram":

        fig=px.histogram(df,x=x)

    elif chart=="Pie Chart":

        fig=px.pie(df,names=x)

    elif chart=="Area Chart":

        fig=px.area(df,x=x,y=y)

    if fig is not None:

        fig.update_layout(

            template="plotly_white",

            height=650,

            font=dict(

                family="Poppins",

                size=15

            ),

            title=dict(

                x=0.5,

                font=dict(size=24)

            )

        )

        return fig.to_html(full_html=False)

    return None