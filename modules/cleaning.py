import os
import pandas as pd

CLEANED_FOLDER = "cleaned"

os.makedirs(CLEANED_FOLDER, exist_ok=True)


def get_dataset_info(filepath):

    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)

    info = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
        "memory": round(df.memory_usage(deep=True).sum()/1024,2),
        "column_info":[]
    }

    for col in df.columns:

        info["column_info"].append({

            "name":col,

            "datatype":str(df[col].dtype),

            "missing":int(df[col].isnull().sum()),

            "unique":int(df[col].nunique())

        })

    return df,info



def clean_dataset(filepath,
                  remove_missing,
                  remove_duplicates,
                  standardize_columns):

    if filepath.endswith(".csv"):
        df=pd.read_csv(filepath)
    else:
        df=pd.read_excel(filepath)

    report={}

    original_rows=len(df)

    if remove_missing:

        before=len(df)

        df=df.dropna()

        report["missing_removed"]=before-len(df)

    else:

        report["missing_removed"]=0

    if remove_duplicates:

        before=len(df)

        df=df.drop_duplicates()

        report["duplicates_removed"]=before-len(df)

    else:

        report["duplicates_removed"]=0

    if standardize_columns:

        df.columns=[

            col.strip().lower().replace(" ","_")

            for col in df.columns

        ]

        report["columns_standardized"]="Yes"

    else:

        report["columns_standardized"]="No"

    filename = "cleaned_" + os.path.basename(filepath)

    cleaned_file = os.path.join(

        CLEANED_FOLDER,

        filename

    )

    # Save in same format as uploaded
    if filepath.lower().endswith(".csv"):

        df.to_csv(cleaned_file, index=False)

    else:

        df.to_excel(cleaned_file, index=False)

    report["cleaned_filename"] = filename

    report["cleaned_file"] = cleaned_file

    report["final_rows"]=len(df)

    report["original_rows"]=original_rows

    report["cleaned_file"]=cleaned_file

    return report