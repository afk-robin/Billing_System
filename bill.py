import csv
import os
import re
from datetime import datetime
import pandas as pd

COMPANY_FILE = "companies.csv"
BILL_FILE = "billbook.csv"
INVOICE_DIR = "invoices"
CGST_RATE = 0.09
SGST_RATE = 0.09

os.makedirs(INVOICE_DIR, exist_ok=True)

def ensure_file(path, headers):
    if not os.path.isfile(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)

ensure_file(COMPANY_FILE, ["CompanyID","Name","Phone","Email"])
ensure_file(BILL_FILE,    ["CompanyID","Items","SubTotal","CGST","SGST","Total","Timestamp"])

def valid_email(addr):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", addr)

def valid_phone(num):
    return re.match(r"^\+?\d{7,15}$", num)

class Company:
    def __init__(self, cid, name, phone, email):
        self.cid = cid
        self.name = name
        self.phone = phone
        self.email = email

    def save(self):
        with open(COMPANY_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([self.cid, self.name, self.phone, self.email])

class Bill:
    def __init__(self, cid, items):
        self.cid = cid
        self.items = items
        self.subtotal = sum(x["price"] * x["qty"] for x in items)
        self.cgst = round(self.subtotal * CGST_RATE, 2)
        self.sgst = round(self.subtotal * SGST_RATE, 2)
        self.total = round(self.subtotal + self.cgst + self.sgst, 2)
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save(self):
        items_str = ";".join(f"{i['name']}@{i['price']:.2f}@{i['qty']}" for i in self.items)
        with open(BILL_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([self.cid, items_str, f"{self.subtotal:.2f}",
                                    f"{self.cgst:.2f}", f"{self.sgst:.2f}", f"{self.total:.2f}", self.time])
        make_invoice(self)

def make_invoice(bill):
    comp = None
    with open(COMPANY_FILE, "r", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["CompanyID"] == str(bill.cid):
                comp = r
                break
    if not comp:
        print("Could not find company for invoice.")
        return
    stamp = bill.time.replace(":", "-").replace(" ", "_")
    name = f"invoice_{bill.cid}_{stamp}.txt"
    path = os.path.join(INVOICE_DIR, name)
    with open(path, "w", encoding="utf-8") as inv:
        inv.write(f"INVOICE\nDate: {bill.time}\n\n")
        inv.write(f"To: {comp['Name']} (ID: {comp['CompanyID']})\n")
        inv.write(f"Phone: {comp['Phone']}\nEmail: {comp['Email']}\n\n")
        inv.write("Items\n-----\n")
        for it in bill.items:
            line = it["price"] * it["qty"]
            inv.write(f"{it['name']} x{it['qty']} @₹{it['price']:.2f} =₹{line:.2f}\n")
        inv.write(f"\nSubtotal: ₹{bill.subtotal:.2f}\n")
        inv.write(f"CGST : ₹{bill.cgst:.2f}\nSGST : ₹{bill.sgst:.2f}\n")
        inv.write(f"Total : ₹{bill.total:.2f}\n")
    print("Invoice saved to", path)

def next_cid():
    with open(COMPANY_FILE, "r", newline="", encoding="utf-8") as f:
        return len(list(csv.reader(f)))

def add_company():
    print("\nAdd a new company")
    nm = input("Name: ").strip()
    ph = input("Phone: ").strip()
    em = input("Email: ").strip()
    if not valid_phone(ph):
        print("Bad phone format"); return
    if not valid_email(em):
        print("Bad email"); return
    cid = next_cid()
    Company(cid, nm, ph, em).save()
    print("Company added with ID", cid)

def list_companies():
    print("\nCompanies")
    with open(COMPANY_FILE, "r", newline="", encoding="utf-8") as f:
        for r in csv.reader(f):
            print(r[0], "-", r[1])
    print()

def add_purchase():
    list_companies()
    try:
        cid = int(input("Choose company ID: ").strip())
    except:
        print("Invalid"); return
    items = []
    print("Enter products (leave blank name to finish):")
    while True:
        nm = input(" Product name: ").strip()
        if not nm: break
        try:
            pr = float(input(" Price       : ").strip())
            qt = int(input(" Quantity    : ").strip())
        except:
            print("Try again"); continue
        items.append({"name": nm, "price": pr, "qty": qt})
    if not items:
        print("No items"); return
    Bill(cid, items).save()

def show_all():
    print("\nAll purchases")
    h = ["CID","Items","Sub","CGST","SGST","Tot","Time"]
    print("\t".join(h))
    with open(BILL_FILE, "r", newline="", encoding="utf-8") as f:
        for r in csv.reader(f):
            print("\t".join(r))
    print()

def show_for_company():
    list_companies()
    cid = input("Company ID: ").strip()
    print(f"\nPurchases for {cid}")
    h = ["Items","Sub","CGST","SGST","Tot","Time"]
    print("\t".join(h))
    with open(BILL_FILE, "r", newline="", encoding="utf-8") as f:
        for r in csv.reader(f):
            if r[0] == cid:
                print("\t".join(r[1:]))
    print()

def make_excel():
    df1 = pd.read_csv(COMPANY_FILE, encoding="utf-8")
    df2 = pd.read_csv(BILL_FILE, encoding="utf-8")
    out = pd.merge(df2, df1, on="CompanyID", how="left")
    cols = ["CompanyID","Name","Phone","Email","Items","SubTotal","CGST","SGST","Total","Timestamp"]
    out[cols].to_excel("Billing_Report.xlsx", index=False)
    print("Excel report created")

def delete_company():
    list_companies()
    cid = input("Enter ID to remove: ").strip()
    ok = input("Are you sure? (y/n): ").lower()
    if ok != "y": return
    comp_list = [r for r in csv.reader(open(COMPANY_FILE, encoding="utf-8")) if r[0]!=cid]
    with open(COMPANY_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(comp_list)
    bill_list = [r for r in csv.reader(open(BILL_FILE, encoding="utf-8")) if r[0]!=cid]
    with open(BILL_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(bill_list)
    for fn in os.listdir(INVOICE_DIR):
        if fn.startswith(f"invoice_{cid}_"):
            os.remove(os.path.join(INVOICE_DIR, fn))
    print("Company", cid, "and its data deleted")

def main_menu():
    while True:
        print("""
1) Add company
2) View companies
3) Add purchase
4) View all purchases
5) View purchases by company
6) Excel report
7) Delete company
8) Exit""")
        choice = input("Your choice: ").strip()
        if choice=="1": add_company()
        elif choice=="2": list_companies()
        elif choice=="3": add_purchase()
        elif choice=="4": show_all()
        elif choice=="5": show_for_company()
        elif choice=="6": make_excel()
        elif choice=="7": delete_company()
        elif choice=="8":
            print("Bye!")
            break
        else:
            print("That won't work, try again.")

if __name__=="__main__":
    main_menu()
