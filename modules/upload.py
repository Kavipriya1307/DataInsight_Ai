import os
import time
import pandas as pd
from datetime import datetime

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_dataset(file):

    filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + file.filename

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)
    start = time.time()
    # ---------- Read Dataset Faster ----------

    if filename.lower().endswith(".csv"):

        df = pd.read_csv(

            filepath,

            low_memory=False

        )

    else:

        df = pd.read_excel(filepath)

    # ---------- Dataset Information ----------

    rows = len(df)

    columns = len(df.columns)

    missing = int(df.isnull().sum().sum())

    duplicates = int(df.duplicated().sum())

    memory = round(

        df.memory_usage(deep=True).sum() / (1024 * 1024),

        2

    )

    preview = df.head(10).to_html(

        classes="table",

        index=False

    )

    summary = {

        "file_name": filename,

        "filepath": filepath,

        "original_name": file.filename,

        "rows": rows,

        "columns": columns,

        "missing": missing,

        "duplicates": duplicates,

        "memory": memory,

        "preview": preview

    }
    end = time.time()

    summary["processing_time"] = round(end-start,2)

    return summary