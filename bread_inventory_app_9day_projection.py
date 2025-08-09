
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("Bread Inventory & PO Dashboard (9-Day Projection)")

uploaded_file = st.file_uploader("Upload Sales CSV", type=["csv"])
if not uploaded_file:
    st.stop()

df = pd.read_csv(uploaded_file, parse_dates=["DATE"])
df["Variant"] = df["Modifier Name"].str.extract(r"(French Baguette|Hero|Medianoche|Multigrain)")
df = df.dropna(subset=["Variant"])
df["Modifier Sold"] = pd.to_numeric(df["Modifier Sold"], errors="coerce").fillna(0).astype(int)
df["Day"] = (df["DATE"] - df["DATE"].min()).dt.days
df["Day Name"] = df["DATE"].dt.day_name()

# Prompt for initial inventory
st.sidebar.header("Initial Inventory")
starting_inventory = {
    "French Baguette": st.sidebar.number_input("French Baguette", 0, 500, 16),
    "Hero": st.sidebar.number_input("Hero", 0, 500, 115),
    "Medianoche": st.sidebar.number_input("Medianoche", 0, 500, 27),
    "Multigrain": st.sidebar.number_input("Multigrain", 0, 500, 22),
}

# Aggregate daily sales
daily_sales = df.groupby(["Day", "Variant"])["Modifier Sold"].sum().unstack(fill_value=0)

# Project day 8 and 9 using average of previous Monday (Day 0) and Tuesday (Day 1)
if 0 in daily_sales.index and 1 in daily_sales.index:
    monday_sales = daily_sales.loc[0]
    tuesday_sales = daily_sales.loc[1]
    projected_extra = ((monday_sales + tuesday_sales) / 2).round().astype(int)
    daily_sales.loc[7] = projected_extra
    daily_sales.loc[8] = projected_extra

daily_sales = daily_sales.sort_index()

# Delivery days (Tuesday, Thursday, Saturday)
delivery_days = [1, 3, 5, 8]
min_inventory = 3
max_inventory = 5

# PO Dashboard logic
po_data = []
inventory = starting_inventory.copy()

for day in range(9):
    po_row = {"Day": day}
    for variant in daily_sales.columns:
        used = daily_sales.loc[day, variant] if day in daily_sales.index else 0
        inventory[variant] -= used

        # Check if a delivery is needed today for future coverage
        if day in delivery_days:
            next_delivery_day = next((d for d in delivery_days if d > day), 9)
            days_to_cover = range(day + 1, next_delivery_day)
            projected = sum(daily_sales.loc[d, variant] for d in days_to_cover if d in daily_sales.index)
            required = max(min_inventory, projected) - inventory[variant]
            order_qty = max(0, min(max_inventory, required))
            inventory[variant] += order_qty
            po_row[variant] = order_qty
        else:
            po_row[variant] = 0
    po_data.append(po_row)

po_df = pd.DataFrame(po_data)
st.subheader("🧾 Purchase Order Plan")
st.dataframe(po_df.set_index("Day"))
