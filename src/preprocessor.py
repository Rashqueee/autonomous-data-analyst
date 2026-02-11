import pandas as pd

def preprocess_dates(df):
    df = df.copy()
    date_columns = []    

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_columns.append(col)
            continue
        if any(x in col.lower() for x in ['date', 'time', 'day']):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].notna().sum() > 0: 
                    date_columns.append(col)
            except:
                pass
    for col in date_columns:
        if col in df.columns and pd.api.types.is_datetime64_any_dtype(df[col]):
            df[f'{col}_year'] = df[col].dt.year
            df[f'{col}_month'] = df[col].dt.month
            df[f'{col}_year_month'] = df[col].dt.to_period('M').astype(str) 
    return df