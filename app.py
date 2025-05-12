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
#by state v

    state_abbrev = { #abbreviating state names
        'IOWA': 'IA',
        'FLORIDA': 'FL',
        'NEBRASKA': 'NE',
        'SOUTH DAKOTA': 'SD',
        'KANSAS': 'KS'}
    
    df['pt_state'] = df['pt_state'].replace(state_abbrev)

    df['pt_state'] = df['pt_state'].astype(str).str.strip().str.upper() #standardizing

    valid_states = {'FL', 'IA', 'NE', 'SD', 'KS'}

    df.loc[~df['pt_state'].isin(valid_states), 'pt_state'] = 'UNKNOWN' #invalid entries go in 'Unknown'

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce') #making sure 'amount' is numeric

    state_df = df[['pt_state', 'amount']].dropna() #drop entries with missing amount

    support_by_state = state_df.groupby('pt_state')['amount'].sum().sort_values(ascending=False) #group and sum by state

    support_by_state.rename(index={'UNKNOWN': 'Unknown'}, inplace=True) #rename for display

    st.write("### Total Support Given by State")
    st.bar_chart(support_by_state)

    st.write("Table (Total $ Support by State):")
    st.dataframe(support_by_state)

####### bar chart & table, support by state ^
####### pie chart, support by state v

    import plotly.express as px

    states = 5
    top_states = support_by_state.head(states)
    other_sum = support_by_state[states:].sum()
    combined = pd.concat([top_states]) #combining the states

    combined_df = combined.reset_index() #resetting index for plotly
    combined_df.columns = ['State', 'Total Support']

    fig = px.pie(combined_df, names='State', values='Total Support', title='Support Distribution % by State (Interactive)', hole=0.1) #interactive pie chart
    
    fig.update_traces(textinfo='label+percent', pull=[0.05]*len(combined_df))

    st.plotly_chart(fig)

########### Pie chart ^

#by state ^
    st.write("---------------")
    st.write("---------------")
#by gender v

########### Bar chart v

    df['gender'] = (
        df['gender']
        .fillna('Unknown')         #make NaNs = Unknown
        .astype(str)
        .str.strip()
        .str.title()                #capitalize words
        .replace({'': 'Unknown'}))  # blanks = Unknown

    gender_support = (              #group by gender and sum amount
     df.groupby('gender')['amount']
     .sum()
     .sort_values(ascending=False))

    st.write("### Total Support Given by Gender") #display chart & table
    st.bar_chart(gender_support)

    st.write("Table (Total $ Support by Gender):")
    st.dataframe(gender_support)

#by gender ^

    st.write("---------------")
    st.write("---------------")
#by age v

#######
    import datetime

    current_year = datetime.datetime.now().year #importing today's year

    def clean_dob(val):
        try:
            date = pd.to_datetime(val, errors='coerce') #use datetime to standardize 'YYYY' and '1/1/YYYY')
            if date is pd.NaT:
                return None
            year = date.year
            if year > current_year or year < 1900:  # getting rid of the typos (2973, 2064)
                return None
            return year
        except:
            return None

    df['dob_clean'] = df['dob'].apply(clean_dob)

    df['age'] = current_year - df['dob_clean'] # calculating their age

    def assign_age_group(age): #putting them in groups for the plot
        if pd.isna(age):
            return 'Unknown'
        elif age < 18:
            return '0–17'
        elif age < 35:
            return '18–34'
        elif age < 50:
            return '35–49'
        elif age < 65:
            return '50–64'
        else:
            return '65+'

    df['age_group'] = df['age'].apply(assign_age_group)

    age_support = (
        df.groupby('age_group')['amount']
        .sum()
        .reindex(['0–17', '18–34', '35–49', '50–64', '65+', 'Unknown']))

    age_counts = (
        df['age_group']
        .value_counts()
        .reindex(['0–17', '18–34', '35–49', '50–64', '65+', 'Unknown'])) #counting number of patients per age group

    st.write("### Total Support Given by Age Group")
    st.bar_chart(age_support)

    st.write("Table (Total $ Support by Age Group):")
    st.dataframe(age_support)

    st.write("Table (Number of Patients by Age Group):")
    st.dataframe(age_counts)

#by age ^
    st.write("---------------")
    st.write("---------------")
#by income v

#######scatterplot v

    import altair as alt

    df['total_household_gross_monthly_income'] = pd.to_numeric(df['total_household_gross_monthly_income'], errors='coerce') #convert income + household size, some cleaning
    df['household_size'] = pd.to_numeric(df['household_size'], errors='coerce')

    df = df[df['household_size'] > 0] #avoiding invalid sizes

    df['per_capita_income'] = df['total_household_gross_monthly_income'] / df['household_size'] #calculating per capita income

    filtered_df = df[(df['per_capita_income'] < 10000) & (df['amount'] < 10000)] #filter out outliers (might not be worth using?)

    st.write("### Relationship Between Income(per capita by household) and Amount of Support Given") #scatterplot using altair

    scatter = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.5).encode(
        x=alt.X('per_capita_income', title='Per Capita Monthly Income (Per Person in Household) ($)'), y=alt.Y('amount', title='Support Amount ($)'), tooltip=['per_capita_income', 'amount']
    ).properties(
        width=700,
        height=400,
        title='Scatter Plot: Income vs Support Amount')

    st.altair_chart(scatter)

##################################### scatter ^------v boxplots

    import altair as alt
    import numpy as np

    df['total_household_gross_monthly_income'] = pd.to_numeric(df['total_household_gross_monthly_income'], errors='coerce') #calculating per capita income, some cleaning
    df['household_size'] = pd.to_numeric(df['household_size'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    df = df[df['household_size'] > 0]
    df['per_capita_income'] = df['total_household_gross_monthly_income'] / df['household_size']

    def bin_income(val): #putting the per capita values into ranges
        if pd.isna(val):
            return 'Unknown'
        elif val < 500:
            return '<$500'
        elif val < 1000:
            return '$500–999'
        elif val < 1500:
            return '$1000–1499'
        elif val < 2000:
            return '$1500–1999'
        elif val < 3000:
            return '$2000–2999'
        else:
            return '$3000+'

    df['income_group'] = df['per_capita_income'].apply(bin_income)

    filtered = df[df['amount'].notna() & df['income_group'].notna()]

    st.write("### Support Amounts by Income Group(per capita by household)") 

    box = alt.Chart(filtered).mark_boxplot(extent='min-max', median={'color': 'black'}).encode( #boxplot
        x=alt.X('income_group:N', title='Per Capita Income Group'),
        y=alt.Y('amount:Q', title='Support Amount ($)'),
        color='income_group:N',
    ).properties(
        width=600,
        height=400)

    st.altair_chart(box)

################### boxplot1^
################## boxplot2v

    income_order = ['<$500', '$500–999', '$1000–1499', '$1500–1999', '$2000–2999', '$3000+', 'Unknown'] #making new order

    df['income_group'] = df['per_capita_income'].apply(bin_income)

    base = alt.Chart(filtered).mark_boxplot(extent='min-max', median={'color': 'lightgray'}, ticks=False  #base boxplot with color
    ).encode(
        x=alt.X('income_group:N', sort=income_order, title='Per Capita Income Group'),
        y=alt.Y('amount:Q', title='Support Amount ($)'),
        color=alt.Color('income_group:N', legend=None))

    whiskers = alt.Chart(filtered).mark_rule(color='white').encode( #trying to change the colors of the whiskers so you can see them
        x=alt.X('income_group:N', sort=income_order),
        y='min(amount):Q',
        y2='max(amount):Q')

    boxplot = base + whiskers

    st.altair_chart(boxplot.properties(width=600, height=400))


#by income ^
    st.write("---------------")
    st.write("---------------")
#by insurance v

    df['insurance_type'] = ( #standardizing insurance type into categories
        df['insurance_type']
        .fillna('Unknown')
        .astype(str)
        .str.strip()
        .str.title()
        .replace({
            '': 'Unknown',
            'Missing': 'Unknown',
            'Uninsurred': 'Uninsured',
            'Uninsured': 'Uninsured',
            'Unisured': 'Uninsured',
            'Medicaid & Medicare': 'Medicare & Medicaid',
            'Medicare & Medicaid': 'Medicare & Medicaid'}))

    insurance_support = (
        df.groupby('insurance_type')['amount']
        .sum()
        .sort_values(ascending=False))

    insurance_counts = (
        df['insurance_type']
        .value_counts()
        .reindex(insurance_support.index))  #match order

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  #remove missing amounts
    valid_df = df[df['amount'].notna()]

    support_totals = valid_df.groupby('insurance_type')['amount'].sum() #group and calculate totals
    patient_counts = valid_df.groupby('insurance_type')['amount'].count()

    per_capita_support = (support_totals / patient_counts).sort_values(ascending=False) #calculate per capita support

    #Plots for Insurance Type:

    st.write("### Average Support by Insurance Type")
    st.bar_chart(per_capita_support)

    st.write("Table (Average $ Support by Insurance Type):")
    st.dataframe(per_capita_support)

    st.write("Table (Number of Patients by Insurance Type):")
    st.dataframe(insurance_counts)

    st.write("### Total $ Support Given by Insurance Type")
    st.bar_chart(insurance_support)

    st.write("Table (Total $ Support by Insurance Type):")
    st.dataframe(insurance_support)

elif page == "Time to Send Support":
    st.subheader("Time Between Request and Support")

    import pandas as pd
    import altair as alt

    df['grant_req_date'] = pd.to_datetime(df['grant_req_date'], errors='coerce') #cleaning columns
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

    st.write("### Summary Statistics")
    st.write(response_df['days_to_payment'].describe()) #table summary

    st.write("* Excluding responses of No & Yes (they didn't provide a date)")

elif page == "Unused Grants & Averages":
    st.subheader("Remaining Grant Amounts, Average Amount Given by Type of Assistance")

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce') #cleaning amount column
    df['remaining_balance'] = pd.to_numeric(df['remaining_balance'], errors='coerce')
    df['app_year'] = pd.to_numeric(df['app_year'], errors='coerce')

    unused_df = df[df['remaining_balance'] > 0] #find patients with balance > 0

    unused_by_year = unused_df.groupby('app_year')['patient_id#'].count() #group by year

    patients_with_remaining = ( #counting patients by year
        unused_df.groupby('app_year')['patient_id#']
        .count()
        .sort_index())

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

    df['type_of_assistance_class'] = df['type_of_assistance_class'].astype(str).str.strip().str.title() #cleaning assistance type column

    avg_amount_by_type = ( #calculating average
        df.groupby('type_of_assistance_class')['amount']
        .mean()
        .sort_values(ascending=False))

    st.write("### Average Amount Given by Assistance Type")
    st.bar_chart(avg_amount_by_type)

    st.dataframe(avg_amount_by_type)

elif page == "Impact Summary":
    st.subheader("Past Year Report for Stakeholders")

    df['grant_req_date'] = pd.to_datetime(df['grant_req_date'], errors='coerce') #cleaning the column
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['type_of_assistance_class'] = df['type_of_assistance_class'].astype(str).str.strip().str.title()

    summary_choice = st.selectbox(
        "Select Timeframe for Summary:",
        ["Since May 13, 2024", "Calendar Year 2025", "Calendar Year 2024"]) #setting options for selectbox

    if summary_choice == "Since May 13, 2024": #selectbox filters
        start_date = pd.Timestamp("2024-05-13")
        filtered_df = df[df['grant_req_date'] >= start_date]
        label = "Since May 13, 2024"

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

    st.write(f"## Summary – {label}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Patients Supported", f"{total_patients:,}")
    col2.metric("Total Amount Granted", f"${total_amount:,.2f}")
    col3.metric("Average Grant Per Patient", f"${avg_grant:,.2f}")

    st.write(f"### Types of Assistance – {label}")
    st.dataframe(top_assistance.rename("Number of Patients"))
