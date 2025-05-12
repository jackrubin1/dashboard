import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import datetime

st.set_page_config(page_title="Hope Foundation Dashboard", layout="centered")

def load_data():
    url = 'https://raw.githubusercontent.com/jackrubin1/dashboard/main/cleaned_data.csv'
    df = pd.read_csv(url)
    return df

df = load_data()

df['amount'] = pd.to_numeric(df['amount'], errors='coerce') #cleaning up columns I plan to use
df['grant_req_date'] = pd.to_datetime(df['grant_req_date'], errors='coerce')
df['type_of_assistance_class'] = df['type_of_assistance_class'].astype(str).str.strip().str.title()


st.title("Hope Foundation Dashboard")

st.sidebar.title("Page Select:")
page = st.sidebar.radio("Go to",
    ["Ready for Review",
    "Support by Demographics",
    "Time to Send Support",
    "Unused Grants",
    "Stakeholder Summary"])

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

    demographic_option = st.selectbox("Choose a Demographic Category:", ["State", "Gender", "Age", "Income", "Insurance Type"]) #filter

    if demographic_option == "State":
        state_abbrev = {'IOWA': 'IA', 'FLORIDA': 'FL', 'NEBRASKA': 'NE','SOUTH DAKOTA': 'SD', 'KANSAS': 'KS'} #normalizing state names
        df['pt_state'] = df['pt_state'].replace(state_abbrev)
        df['pt_state'] = df['pt_state'].astype(str).str.strip().str.upper()
        valid_states = {'FL', 'IA', 'NE', 'SD', 'KS'}
        df.loc[~df['pt_state'].isin(valid_states), 'pt_state'] = 'UNKNOWN'
        state_df = df[['pt_state', 'amount']].dropna()
        support_by_state = state_df.groupby('pt_state')['amount'].sum().sort_values(ascending=False)
        support_by_state.rename(index={'UNKNOWN': 'Unknown'}, inplace=True)

        top_states = support_by_state
        combined_df = top_states.reset_index()
        combined_df.columns = ['State', 'Total Support']
        fig = px.pie(combined_df, names='State', values='Total Support', title='Support Distribution % by State (Interactive)', hole=0.1)
        fig.update_traces(textinfo='label+percent', pull=[0.05]*len(combined_df))
        st.plotly_chart(fig)

        st.write("Support Distribution per State by $ Amount")

        st.bar_chart(support_by_state)
        st.dataframe(support_by_state)

    elif demographic_option == "Gender":
        df['gender'] = (df['gender'].fillna('Unknown').astype(str).str.strip().str.title().replace({'': 'Unknown'})) #normalizing gender
        gender_support = df.groupby('gender')['amount'].sum().sort_values(ascending=False)

        st.write("### Total Support Distribution per Gender by $ Amount")

        st.bar_chart(gender_support)
        st.dataframe(gender_support)

    elif demographic_option == "Age": #normalizing age with datetime

        current_year = datetime.datetime.now().year
        def clean_dob(val):
            try:
                date = pd.to_datetime(val, errors='coerce')
                if date is pd.NaT:
                    return None
                year = date.year
                if year > current_year or year < 1900: #excluding typos
                    return None
                return year
            except:
                return None
        df['dob_clean'] = df['dob'].apply(clean_dob)
        df['age'] = current_year - df['dob_clean']
        def assign_age_group(age):
            if pd.isna(age): return 'Unknown'
            elif age < 18: return '0–17'
            elif age < 35: return '18–34'
            elif age < 50: return '35–49'
            elif age < 65: return '50–64'
            else: return '65+'
        df['age_group'] = df['age'].apply(assign_age_group)
        age_support = df.groupby('age_group')['amount'].sum().reindex(['0–17', '18–34', '35–49', '50–64', '65+', 'Unknown'])
        age_counts = df['age_group'].value_counts().reindex(['0–17', '18–34', '35–49', '50–64', '65+', 'Unknown'])

        st.write("## Total $ Support by Age Group:")
        st.bar_chart(age_support)
        st.dataframe(age_support)
        st.write(" ## Number of Patients by Age Group:")
        st.dataframe(age_counts)

    elif demographic_option == "Income":

        df['total_household_gross_monthly_income'] = pd.to_numeric(df['total_household_gross_monthly_income'], errors='coerce')
        df['household_size'] = pd.to_numeric(df['household_size'], errors='coerce')
        df = df[df['household_size'] > 0]
        df['per_capita_income'] = df['total_household_gross_monthly_income'] / df['household_size']
        filtered_df = df[(df['per_capita_income'] < 10000) & (df['amount'] < 10000)]
        scatter = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.5).encode(
            x=alt.X('per_capita_income', title='Per Capita Monthly Household Income ($)'),
            y=alt.Y('amount', title='Support Amount ($)'),
            tooltip=['per_capita_income', 'amount']).properties(width=700, height=400, title='Average Household Income vs Support Amount')
        st.altair_chart(scatter)

    elif demographic_option == "Insurance Type":
        df['insurance_type'] = (
            df['insurance_type'].fillna('Unknown').astype(str).str.strip().str.title() #normalizing insurance, putting typos in 'unknown'
            .replace({'': 'Unknown', 'Missing': 'Unknown',
                'Uninsurred': 'Uninsured', 'Unisured': 'Uninsured',
                'Medicaid & Medicare': 'Medicare & Medicaid'}))
        
        valid_df = df[df['amount'].notna()]
        support_totals = valid_df.groupby('insurance_type')['amount'].sum()
        patient_counts = valid_df.groupby('insurance_type')['amount'].count()
        per_capita_support = (support_totals / patient_counts).sort_values(ascending=False)
        insurance_counts = df['insurance_type'].value_counts().reindex(per_capita_support.index)

        st.write("# Support by Insurance Type:")

        col1, col2 = st.columns(2)
        with col1:
            st.write("Average $ Support by Insurance Type")
            st.dataframe(per_capita_support)
        with col2:
            st.write("Number of Patients by Insurance Type")
            st.dataframe(insurance_counts)

        st.write("### Total $ Support by Insurance Type")
        st.bar_chart(support_totals.sort_values(ascending=False))  

        st.write("### Average $ Support by Insurance Type")
        st.bar_chart(per_capita_support)  

elif page == "Time to Send Support":

    st.subheader("How long does it normally take to receive support?")

    df['payment_submitted?'] = df['payment_submitted?'].astype(str).str.strip().str.lower()

    date_mask = df['payment_submitted?'].str.contains(r'\d{4}-\d{2}-\d{2}') #filter to date strings
    response_df = df[date_mask].copy()

    response_df['payment_date'] = pd.to_datetime(response_df['payment_submitted?'], errors='coerce') #convert to datetime

    response_df['days_to_payment'] = (response_df['payment_date'] - response_df['grant_req_date']).dt.days #calculating difference in days

    response_df = response_df[response_df['days_to_payment'] > 0] #get rid of invalid values

    st.write("### Time Between Request and Payment (in Days)") #histogram
    hist = alt.Chart(response_df).mark_bar().encode(
        alt.X('days_to_payment', bin=alt.Bin(maxbins=30), title='Days to Receive Payment'),
        alt.Y('count()', title='Number of Patients')).properties(width=700, height=400)

    st.altair_chart(hist)
    summary = response_df['days_to_payment'].describe() #summary table
    selected_stats = summary.drop(['25%', '50%', '75%']) #dropping irrelevant stats from table
    st.write(selected_stats)

    st.write("* Excluding responses of No & Yes to 'payment_submitted?' (Date Not Provided)")
    st.write("* count = number of respondents applicable; mean = average; std = standard deviation")

elif page == "Unused Grants": 
    
    st.subheader("Leftover Grants")

    df['remaining_balance'] = pd.to_numeric(df['remaining_balance'], errors='coerce')
    df['app_year'] = pd.to_numeric(df['app_year'], errors='coerce')

    unused_df = df[df['remaining_balance'] > 0] #find patients with balance > 0

    unused_by_year = unused_df.groupby('app_year')['patient_id#'].count() #group by year

    patients_with_remaining = (
        unused_df.groupby('app_year')['patient_id#']
        .count()
        .rename('Number of Patients') #renaming so it doesn't say 'PatientID#' which is what it was counting.
        .sort_index())

    st.write("### Number of Patients With Unused Grant Funds (by Application Year)")
    st.bar_chart(patients_with_remaining)
    st.dataframe(patients_with_remaining)

    avg_remaining_by_year = ( #finding average remaining balance
        unused_df.groupby('app_year')['remaining_balance']
        .mean()
        .sort_index())

    st.write("### Average Remaining Balance (If balance > 0)")
    st.bar_chart(avg_remaining_by_year)

    st.dataframe(avg_remaining_by_year)

    avg_amount_by_type = ( #calculating average
        df.groupby('type_of_assistance_class')['amount']
        .mean()
        .sort_values(ascending=False))

    st.write("### Average Amount Given by Type of Assistance")
    st.bar_chart(avg_amount_by_type)

    st.dataframe(avg_amount_by_type)

elif page == "Stakeholder Summary":
    st.subheader("Past Year Report for Stakeholders")

    summary_choice = st.selectbox(
        "Select Timeframe for Summary:",
        ["Past 12 Months", "Calendar Year 2025", "Calendar Year 2024"]) #setting options for selectbox

    today = pd.Timestamp.today()
    one_year_ago = today - pd.DateOffset(years=1)

    if summary_choice == "Past 12 Months": #setting up selectbox filters, updated to take from past 12 months
        filtered_df = df[df['grant_req_date'] >= one_year_ago]
        label = f"Past 12 Months (since {one_year_ago.date()})"

    elif summary_choice == "Calendar Year 2025":
        filtered_df = df[df['grant_req_date'].dt.year == 2025]
        label = "Calendar Year 2025"

    else:
        filtered_df = df[df['grant_req_date'].dt.year == 2024]
        label = "Calendar Year 2024"

    total_patients = filtered_df['patient_id#'].nunique()
    total_amount = filtered_df['amount'].sum()
    avg_grant = total_amount / total_patients if total_patients else 0
    top_assistance = filtered_df['type_of_assistance_class'].value_counts() #calculations

    st.write(f"### Summary – {label}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Patients Supported", f"{total_patients:,}")
    col2.metric("Total Amount Granted", f"${total_amount:,.2f}")
    col3.metric("Average Grant Per Patient", f"${avg_grant:,.2f}")

    st.write(f"### Types of Assistance – {label}")
    st.dataframe(top_assistance.rename("Number of Patients"))
