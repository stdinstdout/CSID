import pandas as pd

import base64
import io


def parse_cols_name(content, filename) -> list:
    
    content_type, content_string = content.split(',')

    decoded = base64.b64decode(content_string)
    try:
        data = io.StringIO(decoded.decode('utf-8'))
        if 'csv' in filename:
            df = pd.read_csv(data)
            names = df.columns
        elif 'txt' in filename:
            df = pd.read_table(data)
            names = df.columns
        elif 'xmls' in filename:
            pass
        else:
            return []
    except Exception as e:
        return str(e)

    return [{'label': x, 'value': x} for x in names]


def parse_df_from_content(content, filename):
    content_type, content_string = content.split(',')

    decoded = base64.b64decode(content_string)

    data = io.StringIO(decoded.decode('utf-8'))
    if 'csv' in filename:
        df = pd.read_csv(data)
    elif 'txt' in filename:
        df = pd.read_table(data)
    elif 'xmls' in filename:
        pass
    else:
        raise Exception("File format is not supported")

    return df