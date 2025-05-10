import streamlit as st
import pandas as pd


def load_data():
    url = 'https://raw.githubusercontent.com/jackrubin1/dashboard/main/cleaned_data.csv'
    df = pd.read_csv(url)
    return df

df = load_data()

st.set_page_config(page_title="Hope Foundation Dashboard", layout="centered")

st.title("Hope Foundation Dashboard")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to",
    ["Ready for Review",
    "Support by Demographics",
    "Time to Send Support",
    "Unused Grants & Averages",
    "Impact Summary"])

if page == "Ready for Review":
    st.subheader("Applications Ready for Review")

elif page == "Support by Demographics":
    st.subheader("Support Distribution by Demographics")

elif page == "Time to Send Support":
    st.subheader("Time Between Request and Support")

elif page == "Unused Grants & Averages":
    st.subheader("Grant Usage and Assistance Averages")

elif page == "Impact Summary":
    st.subheader("Yearly Impact Summary for Stakeholders")