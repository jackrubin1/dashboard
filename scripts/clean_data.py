import pandas as pd
from datetime import datetime

url = 'https://github.com/jackrubin1/dashboard/raw/main/UNO%20Service%20Learning%20Data%20Sheet%20De-Identified%20Version.xlsx'
df = pd.read_excel(url)

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_") #standardizing column names

df.dropna(how='all', inplace=True) #get rid of empty rows

date_columns = ['grant_req_date']  #converting dates to datetime format to make stuff easier later
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

yes_no_columns = ['payment_submitted?', 'application_signed?'] #Converting yes/no answers to boolean values
for col in yes_no_columns:
    if col in df.columns:
        df[col] = df[col].str.strip().str.lower().map({'yes': True, 'no': False})

df.to_csv('cleaned_data.csv', index=False)
