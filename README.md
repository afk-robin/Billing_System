Billing Management System — Company-Wise Purchase Tracker with Tax & Excel Reports
This Python-based billing system allows businesses to manage company records, track item-wise purchases, apply GST (CGST & SGST), generate plain-text invoices, and export summarized billing data into Excel format using `pandas`.
- Add,view,and delete companies (ID, name, phone, email)
- Record purchases for companies with multiple items
- Automatically calculate:
- **CGST @ 9%**
- **SGST @ 9%**
- Generates clean `.txt` invoice per bill in `invoices/` folder
- Maintains central CSV record in `billbook.csv`
- Exports all billing + company info into `Billing_Report.xlsx`
