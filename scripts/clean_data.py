import pandas as pd
import glob
import os

excel_files = glob.glob("*.xlsx") #find most recent .xlsx file
if not excel_files:
    raise FileNotFoundError("No Excel files found in the repository directory.")

latest_file = max(excel_files, key=os.path.getmtime)
print(f"Processing most recent Excel file: {latest_file}")

df = pd.read_excel(latest_file)

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "") #standardizing column names

df.dropna(how='all', inplace=True) #dropping empty rows

date_columns = ['grant_req_date'] #fixing dates
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

yes_no_columns = ['payment_submitted?', 'application_signed?'] #standardizing responses
for col in yes_no_columns:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.lower().replace({
            'yes': 'Yes',
            'no': 'No',
            'missing': 'Missing',
            'n/a': 'N/A',
            '': 'Missing'})

output_file = "cleaned_data.csv"
df.to_csv(output_file, index=False)
print(f"Saved cleaned data to: {output_file}")
