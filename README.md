# Bread Inventory & PO Dashboard (9-Day)

This Streamlit app generates purchase orders for four bread types based on real-time sales data.

## 📦 Features
- Projects inventory for 9 days
- Uses past Monday/Tuesday sales to project Days 8 and 9
- Considers deliveries on Tue, Thu, Sat at 9:00 AM
- Avoids early morning shortages

## ▶️ How to Run
```bash
pip install -r requirements.txt
streamlit run bread_inventory_app_9day_projection.py
```

## 🧪 CSV Format
- `DATE` (e.g., 2025-08-04)
- `Modifier Name` (includes bread variant)
- `Modifier Sold` (units sold)
