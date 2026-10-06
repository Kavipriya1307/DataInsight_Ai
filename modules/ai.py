import os
import json
import pandas as pd

from dotenv import load_dotenv
from groq import Groq

# ---------------------------------
# Load Environment Variables
# ---------------------------------

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------------------------------
# Read Dataset
# ---------------------------------

def load_dataset(filepath):

    if filepath.endswith(".csv"):

        return pd.read_csv(filepath, low_memory=False)

    elif filepath.endswith(".xlsx"):

        return pd.read_excel(filepath)

    else:

        raise Exception("Unsupported File Format")

# ---------------------------------
# Dataset Summary
# ---------------------------------

def dataset_summary(df):

    numeric = df.select_dtypes(include="number").columns.tolist()

    categorical = df.select_dtypes(exclude="number").columns.tolist()

    summary = {

        "Rows": int(df.shape[0]),

        "Columns": int(df.shape[1]),

        "Numeric Columns": len(numeric),

        "Categorical Columns": len(categorical),

        "Missing Values": int(df.isnull().sum().sum()),

        "Duplicate Rows": int(df.duplicated().sum())

    }

    return summary

# ---------------------------------
# Convert Summary to Text
# ---------------------------------

def summary_to_text(summary):

    text = ""

    for key, value in summary.items():

        text += f"{key}: {value}\n"

    return text

# ---------------------------------
# Create Prompt
# ---------------------------------

def create_prompt(summary, ml_result=None):

    prompt = f"""

You are a Senior Business Data Analyst.

Below is the dataset summary.

{summary_to_text(summary)}

"""

    if ml_result:

        prompt += f"""

Machine Learning Result

{json.dumps(ml_result, indent=4)}

"""

    prompt += """

Generate a professional business report.

Include exactly these sections.

1. Executive Summary

2. Dataset Overview

3. Key Business Insights

4. Data Quality Analysis

5. Machine Learning Interpretation

6. Business Recommendations

7. Future Scope

Use headings.

Write in simple professional English.

"""

    return prompt

# ---------------------------------
# Generate AI Story
# ---------------------------------

def generate_ai_story(summary, ml_result=None):

    try:

        prompt = create_prompt(summary, ml_result)

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role": "system",
                    "content": "You are a professional Business Intelligence expert who creates executive reports."
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.4,

            max_tokens=1800

        )

        return response.choices[0].message.content

    except Exception as e:

        return f"""
AI Story Generation Failed.

Reason:

{str(e)}
"""


# ---------------------------------
# Complete AI Insight
# ---------------------------------

def generate_complete_insight(filepath, ml_result=None):

    df = load_dataset(filepath)

    summary = dataset_summary(df)

    story = generate_ai_story(

        summary,

        ml_result

    )

    return {

        "summary": summary,

        "story": story,

        "ml_result": ml_result

    }

# ---------------------------------
# Dataset Chat Assistant
# ---------------------------------

def dataset_chat(question, df):

    try:

        sample_data = df.head(10).to_string(index=False)

        statistics = df.describe(include="all").fillna("").to_string()

        prompt = f"""

You are an expert AI Data Analyst.

Below is a sample of the dataset.

{sample_data}

Dataset Statistics

{statistics}

User Question:

{question}

Answer the question accurately using only the dataset information.

If the answer cannot be determined from the dataset, clearly mention that.

Keep the answer professional and concise.

"""

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role":"system",
                    "content":"You answer questions based only on the uploaded dataset."
                },

                {
                    "role":"user",
                    "content":prompt
                }

            ],

            temperature=0.3,

            max_tokens=700

        )

        return response.choices[0].message.content

    except Exception as e:

        return f"""

Unable to answer the question.

Reason:

{str(e)}

"""


# ---------------------------------
# Explain ML Result
# ---------------------------------

def explain_ml_result(ml_result):

    try:

        prompt = f"""

You are a Machine Learning expert.

Analyze the following ML Result.

{json.dumps(ml_result, indent=4)}

Explain:

1. Model Performance

2. Whether the model is reliable

3. Business Meaning

4. Strengths

5. Improvements

Use professional English.

"""

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role":"system",
                    "content":"You explain machine learning models to business users."
                },

                {
                    "role":"user",
                    "content":prompt
                }

            ],

            temperature=0.4,

            max_tokens=900

        )

        return response.choices[0].message.content

    except Exception as e:

        return f"""

ML Explanation Failed.

Reason:

{str(e)}

"""


# ---------------------------------
# Feature Importance Explanation
# ---------------------------------

def explain_feature_importance(feature_importance):

    try:

        prompt = f"""

Feature Importance Values

{json.dumps(feature_importance, indent=4)}

Explain:

• Which feature is most important

• Which feature has least impact

• Business interpretation

• Recommendations

Use professional English.

"""

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role":"system",
                    "content":"You explain feature importance professionally."
                },

                {
                    "role":"user",
                    "content":prompt
                }

            ],

            temperature=0.4,

            max_tokens=700

        )

        return response.choices[0].message.content

    except Exception as e:

        return f"""

Feature Importance Explanation Failed.

Reason:

{str(e)}

"""
    
# ---------------------------------
# Prediction Explanation
# ---------------------------------

def explain_prediction(prediction):

    try:

        prompt = f"""

You are an AI Prediction Analyst.

Prediction Result:

{prediction}

Explain the following:

1. What does this prediction mean?

2. Business Interpretation

3. Possible Real-world Applications

4. Recommendations

Write in professional English.

"""

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role":"system",
                    "content":"You explain prediction results professionally."
                },

                {
                    "role":"user",
                    "content":prompt
                }

            ],

            temperature=0.4,

            max_tokens=700

        )

        return response.choices[0].message.content

    except Exception as e:

        return f"""

Prediction Explanation Failed.

Reason:

{str(e)}

"""


# ---------------------------------
# Visualization Explanation
# ---------------------------------

def explain_visualization(chart_name, chart_data):

    try:

        prompt = f"""

Chart Name:

{chart_name}

Chart Information:

{chart_data}

Explain:

1. What this chart represents

2. Key Trends

3. Business Insights

4. Recommendations

Keep the explanation simple and professional.

"""

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role":"system",
                    "content":"You are an expert Data Visualization Analyst."
                },

                {
                    "role":"user",
                    "content":prompt

                }

            ],

            temperature=0.4,

            max_tokens=700

        )

        return response.choices[0].message.content

    except Exception as e:

        return f"""

Visualization Explanation Failed.

Reason:

{str(e)}

"""