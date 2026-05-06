import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sqlite3

# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
    color: white;
}

h1, h2, h3, h4 {
    color: white;
}

[data-testid="metric-container"] {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
}

section[data-testid="stSidebar"] {
    background-color: #161A23;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# CREATE FOLDERS
# -------------------------------------------------

os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("database", exist_ok=True)

# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title("💸 Personal Expense Tracker Dashboard")
st.markdown("### Smart Financial Analytics & Expense Visualization System")

st.markdown("---")

# -------------------------------------------------
# SAMPLE DATASET
# -------------------------------------------------

sample_data = {
    "Date": [
        "2026-01-01", "2026-01-02", "2026-01-03",
        "2026-01-04", "2026-01-05", "2026-01-06",
        "2026-01-07", "2026-01-08", "2026-01-09",
        "2026-01-10", "2026-01-11", "2026-01-12"
    ],

    "Category": [
        "Food", "Transport", "Shopping",
        "Bills", "Entertainment", "Food",
        "Transport", "Shopping", "Bills",
        "Food", "Healthcare", "Education"
    ],

    "Amount": [
        250, 120, 1500,
        2200, 800, 300,
        100, 2500, 1800,
        450, 700, 1200
    ],

    "Payment_Method": [
        "UPI", "Cash", "Card",
        "UPI", "Card", "Cash",
        "UPI", "Card", "UPI",
        "Cash", "Card", "UPI"
    ],

    "Description": [
        "Lunch", "Bus Fare", "Clothes",
        "Electricity Bill", "Movie",
        "Dinner", "Metro",
        "Shoes", "Internet Bill",
        "Snacks", "Medicine", "Course Fee"
    ]
}

sample_df = pd.DataFrame(sample_data)

sample_df.to_csv("data/expenses.csv", index=False)

# -------------------------------------------------
# SQLITE DATABASE CONNECTION
# -------------------------------------------------

conn = sqlite3.connect(
    "database/expenses.db",
    check_same_thread=False
)

cursor = conn.cursor()


# -------------------------------------------------
# CREATE TABLE
# -------------------------------------------------

cursor.execute("""

CREATE TABLE IF NOT EXISTS expenses (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    Date TEXT,

    Category TEXT,

    Amount REAL,

    Payment_Method TEXT,

    Description TEXT

)

""")

conn.commit()
# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("📂 Expense Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload Expense CSV",
    type=["csv"]
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("CSV Uploaded Successfully")

else:
    df = pd.read_csv("data/expenses.csv")
    st.sidebar.info("Using Sample Dataset")
    
# -------------------------------------------------
# SAVE DATA TO SQLITE
# -------------------------------------------------

df.to_sql(
    "expenses",
    conn,
    if_exists="replace",
    index=False
)

# -------------------------------------------------
# DATA CLEANING
# -------------------------------------------------

df.dropna(inplace=True)

df["Date"] = pd.to_datetime(df["Date"])

df["Month"] = df["Date"].dt.month_name()

# -------------------------------------------------
# MANUAL EXPENSE ENTRY
# -------------------------------------------------

st.sidebar.markdown("---")

st.sidebar.subheader("➕ Add New Expense")

expense_date = st.sidebar.date_input("Date")

expense_category = st.sidebar.selectbox(
    "Category",
    [
        "Food",
        "Transport",
        "Shopping",
        "Bills",
        "Entertainment",
        "Healthcare",
        "Education"
    ]
)

expense_amount = st.sidebar.number_input(
    "Amount",
    min_value=1.0
)

expense_payment = st.sidebar.selectbox(
    "Payment Method",
    ["UPI", "Cash", "Card"]
)

expense_description = st.sidebar.text_input(
    "Description"
)

if st.sidebar.button("Add Expense"):

    cursor.execute("""

    INSERT INTO expenses (
        Date,
        Category,
        Amount,
        Payment_Method,
        Description
    )

    VALUES (?, ?, ?, ?, ?)

    """, (

        str(expense_date),
        expense_category,
        expense_amount,
        expense_payment,
        expense_description

    ))

    conn.commit()

    st.sidebar.success("Expense Added Successfully")

    st.rerun()

# -------------------------------------------------
# FILTERS
# -------------------------------------------------

st.sidebar.subheader("🔍 Filters")

selected_category = st.sidebar.multiselect(
    "Select Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

selected_payment = st.sidebar.multiselect(
    "Select Payment Method",
    options=df["Payment_Method"].unique(),
    default=df["Payment_Method"].unique()
)
db_df = pd.read_sql_query(
    "SELECT * FROM expenses",
    conn
)

db_df["Date"] = pd.to_datetime(db_df["Date"])

db_df["Month"] = db_df["Date"].dt.month_name()

filtered_df = df[
    (df["Category"].isin(selected_category)) &
    (df["Payment_Method"].isin(selected_payment))
]
if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------

st.markdown("## 📊 Financial Overview")

total_spending = filtered_df["Amount"].sum()

if filtered_df.empty:
    average_spending = 0
else:
    average_spending = filtered_df["Amount"].mean()

if filtered_df.empty:
    highest_category = "No Data"
else:
    highest_category = (
        filtered_df.groupby("Category")["Amount"]
        .sum()
        .idxmax()
    )

total_transactions = len(filtered_df)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Spending",
    f"₹{total_spending:,.0f}"
)

col2.metric(
    "📈 Average Spending",
    f"₹{average_spending:,.0f}"
)

col3.metric(
    "🔥 Highest Category",
    highest_category
)

col4.metric(
    "🧾 Transactions",
    total_transactions
)

st.markdown("---")

# -------------------------------------------------
# DATA PREVIEW
# -------------------------------------------------

st.markdown("## 📋 Expense Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=300
)

# -------------------------------------------------
# CHARTS
# -------------------------------------------------

col_left, col_right = st.columns(2)

# -------------------------------------------------
# CATEGORY BAR CHART
# -------------------------------------------------

with col_left:

    st.markdown("## 📌 Category-wise Spending")

    category_analysis = (
        filtered_df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
    )

    fig_bar = px.bar(
        category_analysis,
        x="Category",
        y="Amount",
        text_auto=True,
        title="Expense by Category"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

# -------------------------------------------------
# PAYMENT METHOD PIE CHART
# -------------------------------------------------

with col_right:

    st.markdown("## 💳 Payment Method Distribution")

    payment_analysis = (
        filtered_df.groupby("Payment_Method")["Amount"]
        .sum()
        .reset_index()
    )

    fig_pie = px.pie(
        payment_analysis,
        names="Payment_Method",
        values="Amount",
        hole=0.5,
        title="Payment Method Analysis"
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# -------------------------------------------------
# MONTHLY TREND
# -------------------------------------------------

st.markdown("## 📅 Monthly Spending Trend")

monthly_analysis = (
    filtered_df.groupby("Month")["Amount"]
    .sum()
    .reset_index()
)

fig_line = px.line(
    monthly_analysis,
    x="Month",
    y="Amount",
    markers=True,
    title="Monthly Expense Trend"
)

st.plotly_chart(
    fig_line,
    use_container_width=True
)

# -------------------------------------------------
# DAILY TREND
# -------------------------------------------------

st.markdown("## 📈 Daily Spending Analysis")

daily_spending = (
    filtered_df.groupby("Date")["Amount"]
    .sum()
    .reset_index()
)

fig_daily = px.area(
    daily_spending,
    x="Date",
    y="Amount",
    title="Daily Spending Trend"
)

st.plotly_chart(
    fig_daily,
    use_container_width=True
)

# -------------------------------------------------
# SUMMARY TABLES
# -------------------------------------------------

col5, col6 = st.columns(2)

with col5:

    st.markdown("## 📊 Category Summary")

    category_summary = (
        filtered_df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
    )

    st.dataframe(
        category_summary,
        use_container_width=True
    )

with col6:

    st.markdown("## 💳 Payment Summary")

    payment_summary = (
        filtered_df.groupby("Payment_Method")["Amount"]
        .sum()
        .reset_index()
    )

    st.dataframe(
        payment_summary,
        use_container_width=True
    )

# -------------------------------------------------
# REPORT GENERATION
# -------------------------------------------------

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

st.markdown("## 📄 Download Financial Report")

report_data = {
    "Metric": [
        "Total Spending",
        "Average Spending",
        "Highest Spending Category",
        "Total Transactions"
    ],

    "Value": [
        f"₹{total_spending:,.2f}",
        f"₹{average_spending:,.2f}",
        highest_category,
        str(total_transactions)
    ]
}

report_df = pd.DataFrame(report_data)

# CSV REPORT

csv_report_path = "reports/summary_report.csv"

report_df.to_csv(csv_report_path, index=False)

# PDF REPORT

pdf_report_path = "reports/expense_report.pdf"

doc = SimpleDocTemplate(
    pdf_report_path,
    pagesize=letter
)

styles = getSampleStyleSheet()

elements = []

title = Paragraph(
    "<b>Personal Expense Tracker Report</b>",
    styles['Title']
)

elements.append(title)

elements.append(Spacer(1, 20))

table_data = [["Metric", "Value"]]

for index, row in report_df.iterrows():

    table_data.append([
        row["Metric"],
        row["Value"]
    ])

table = Table(
    table_data,
    colWidths=[250, 200]
)

table.setStyle(TableStyle([

    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),

    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

    ('GRID', (0, 0), (-1, -1), 1, colors.black),

]))

elements.append(table)

doc.build(elements)

st.success("PDF Report Generated Successfully")

# DOWNLOAD BUTTONS

col1, col2 = st.columns(2)

with col1:

    with open(csv_report_path, "rb") as file:

        st.download_button(
            label="⬇ Download CSV Report",
            data=file,
            file_name="summary_report.csv",
            mime="text/csv"
        )

with col2:

    with open(pdf_report_path, "rb") as pdf_file:

        st.download_button(
            label="⬇ Download PDF Report",
            data=pdf_file,
            file_name="expense_report.pdf",
            mime="application/pdf"
        )

