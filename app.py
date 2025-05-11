import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hope Foundation Dashboard", layout="centered")

def load_data():
    url = 'https://raw.githubusercontent.com/jackrubin1/dashboard/main/cleaned_data.csv'
    df = pd.read_csv(url)
    return df

df = load_data()

st.title("Hope Foundation Dashboard")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to",
    ["Ready for Review",
    "Support by Demographics",
    "Time to Send Support",
    "Unused Grants & Averages",
    "Impact Summary"])

if page == "Ready for Review":
    st.subheader("Applications Ready for Review (Listed as 'Pending')")

    ready_df = df[df['request_status'].str.strip().str.lower() == "pending"] #filter for request_status = 'pending', can replace with 'approved' or 'denied' to replace with those applications

    ready_df['application_signed?'] = ( #group blanks/NaNs into 'missing' - there weren't any 'n/a' under 'pending' so I didn't have to worry about that. Wasn't sure if n/a = missing or if it is literally "not applicable" for that application
        ready_df['application_signed?']
        .fillna('missing')
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({
            '': 'missing'}))

    cleaned_signing_values = sorted(ready_df['application_signed?'].unique()) #get unique cleaned values

    label_map = { #make display labels for sidebar
        'yes': 'Yes',
        'no': 'No',
        'missing': 'Missing'}
    
    label_map = {k: v for k, v in label_map.items() if k in cleaned_signing_values}
    reverse_label_map = {v: k for k, v in label_map.items()}

    selected_labels = st.sidebar.multiselect( #sidebar for application_signed status
        "Has the application been signed?",
        options=list(label_map.values()),
        default=list(label_map.values()))

    selected_statuses = [reverse_label_map[label] for label in selected_labels] #to match lowercase values in the data

    filtered_df = ready_df[ready_df['application_signed?'].isin(selected_statuses)] #filter df based on sidebar

    st.write(f"Showing {len(filtered_df)} applications that are ready for review.") #results
    st.dataframe(filtered_df)

elif page == "Support by Demographics":
    st.subheader("Support Distribution by Demographics")

elif page == "Time to Send Support":
    st.subheader("Time Between Request and Support")

elif page == "Unused Grants & Averages":
    st.subheader("Grant Usage and Assistance Averages")

elif page == "Impact Summary":
    st.subheader("Yearly Impact Summary for Stakeholders")
