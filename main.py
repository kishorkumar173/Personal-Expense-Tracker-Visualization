import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Create folders
os.makedirs("outputs", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# -----------------------------------
# Synthetic Expense Dataset
# -----------------------------------

data = {
    "Date": [
        "2026-01-01", "2026-01-02", "2026-01-03",
        "2026-01-04", "2026-01-05", "2026-01-06",
        "2026-01-07", "2026-01-08", "2026-01-09",
        "2026-01-10"
    ],

    "Category": [
        "Food", "Transport", "Shopping",
        "Bills", "Entertainment", "Food",
        "Transport", "Shopping", "Bills",
        "Food"
    ],

    "Amount": [
        250, 120, 1500,
        2200, 800, 300,
        100, 2500, 1800,
        450
    ],

    "Payment_Method": [
        "UPI", "Cash", "Card",
        "UPI", "Card", "Cash",
        "UPI", "Card", "UPI",
        "Cash"
    ],

    "Description": [
        "Lunch", "Bus Fare", "Clothes",
        "Electricity Bill", "Movie",
        "Dinner", "Metro",
        "Shoes", "Internet Bill",
        "Snacks"
    ]
}

df = pd.DataFrame(data)

# Save dataset
df.to_csv("data/expenses.csv", index=False)

print("Dataset Created Successfully")

# -----------------------------------
# Load Dataset
# -----------------------------------

df = pd.read_csv("data/expenses.csv")

# -----------------------------------
# Data Cleaning
# -----------------------------------

df.dropna(inplace=True)

df["Date"] = pd.to_datetime(df["Date"])

df["Month"] = df["Date"].dt.month_name()

# -----------------------------------
# Category-wise Analysis
# -----------------------------------

category_analysis = df.groupby("Category")["Amount"].sum()

print("\nCategory-wise Spending:")
print(category_analysis)

# -----------------------------------
# Monthly Spending
# -----------------------------------

monthly_analysis = df.groupby("Month")["Amount"].sum()

print("\nMonthly Spending:")
print(monthly_analysis)

# -----------------------------------
# Payment Method Analysis
# -----------------------------------

payment_analysis = df.groupby("Payment_Method")["Amount"].sum()

print("\nPayment Method Analysis:")
print(payment_analysis)

# -----------------------------------
# Highest Spending Category
# -----------------------------------

highest_category = category_analysis.idxmax()

print(f"\nHighest Spending Category: {highest_category}")

# -----------------------------------
# Average Daily Spending
# -----------------------------------

daily_average = df["Amount"].mean()

print(f"\nAverage Daily Spending: ₹{daily_average:.2f}")

# -----------------------------------
# Total Spending
# -----------------------------------

total_spending = df["Amount"].sum()

print(f"\nTotal Spending: ₹{total_spending}")

# -----------------------------------
# Visualization 1
# Category-wise Bar Chart
# -----------------------------------

plt.figure(figsize=(8,5))
sns.barplot(
    x=category_analysis.index,
    y=category_analysis.values
)

plt.title("Category-wise Spending")
plt.xlabel("Category")
plt.ylabel("Amount")

plt.savefig("outputs/category_bar_chart.png")

# -----------------------------------
# Visualization 2
# Monthly Spending Line Chart
# -----------------------------------

plt.figure(figsize=(8,5))

plt.plot(
    monthly_analysis.index,
    monthly_analysis.values,
    marker='o'
)

plt.title("Monthly Spending Trend")
plt.xlabel("Month")
plt.ylabel("Amount")

plt.savefig("outputs/monthly_trend_chart.png")

# -----------------------------------
# Visualization 3
# Payment Method Pie Chart
# -----------------------------------

plt.figure(figsize=(7,7))

plt.pie(
    payment_analysis.values,
    labels=payment_analysis.index,
    autopct='%1.1f%%'
)

plt.title("Payment Method Distribution")

plt.savefig("outputs/payment_method_pie_chart.png")

# -----------------------------------
# Visualization 4
# Daily Spending Trend
# -----------------------------------

daily_spending = df.groupby("Date")["Amount"].sum()

plt.figure(figsize=(10,5))

plt.plot(
    daily_spending.index,
    daily_spending.values,
    marker='o'
)

plt.title("Daily Spending Trend")
plt.xlabel("Date")
plt.ylabel("Amount")

plt.xticks(rotation=45)

plt.savefig("outputs/daily_spending_chart.png")

# -----------------------------------
# Generate Report
# -----------------------------------

report = {
    "Total Spending": [total_spending],
    "Average Daily Spending": [daily_average],
    "Highest Spending Category": [highest_category]
}

report_df = pd.DataFrame(report)
os.makedirs("reports", exist_ok=True)
report_df.to_csv("reports/summary_report.csv", index=False)

print("\nReport Generated Successfully")

print("\nProject Execution Completed")
