import csv
import json

from datetime import datetime


def clean_name(name):

    name = name.split()
    name= " ".join(name).title()
    return name


def clean_amount(amount):
    amount=str(amount).strip().replace(',','')

    try:
        amount=float(amount)
        if amount < 0:
            return None
        
        return amount
    
    
    except ValueError:
        return None
     
     
def clean_date(date):

    date=date.strip()
    formats = ["%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%d"]

    for i in formats:
        try:
            date = datetime.strptime(date, i)
            date=date.strftime("%d-%m-%Y")
            return date
        
        except ValueError:
            pass

    return None


def clean_status(status):
    status=status.strip().lower()
    valid=["paid","pending","cancelled","refund"]

    if status in valid:
        return status

    return None



def check_duplicate(row, duplicate_orders):

    order_id = row["order_id"].strip()

    if order_id in duplicate_orders:

        for duplicate in duplicate_orders[order_id]:

            if duplicate["transaction_id"] == row["transaction_id"]:
                continue

            if (
                clean_name(duplicate["customer_name"]) == clean_name(row["customer_name"])
                and clean_amount(duplicate["amount"]) == clean_amount(row["amount"])
                and clean_date(duplicate["transaction_date"]) == clean_date(row["transaction_date"])
                and clean_status(duplicate["status"]) == clean_status(row["status"])
            ):
                return True

    return False


    

#-----------------------------------------------------------------

with open("input.csv", "r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

cleaned_rows=[]


#To find count of duplicate transactions
transaction_counts = {}

for i in rows:
    transaction_id = i["transaction_id"].strip()

    if transaction_id in transaction_counts:
        transaction_counts[transaction_id] += 1
    else:
        transaction_counts[transaction_id] = 1



#To find Order_id of duplicate transactions
order_counts = {}

for row in rows:
    order_id = row["order_id"].strip()

    if order_id in order_counts:
        order_counts[order_id] += 1
    else:
        order_counts[order_id] = 1


duplicate_orders = {}

for row in rows:
    order_id = row["order_id"].strip()

    if order_counts[order_id] > 1:
        if order_id not in duplicate_orders:
            duplicate_orders[order_id] = []

        duplicate_orders[order_id].append(row)                



#MAIN CLEAN LOOP-------------------------------------------------

for row in rows:

    
    cleaned_name = clean_name(row["customer_name"])

    cleaned_amount= clean_amount(row["amount"])

    cleaned_date=clean_date(row["transaction_date"])

    cleaned_status=clean_status(row["status"])

    order_id = row["order_id"].strip()


    issues = []

   
    #for Transaction_id
    transaction_id = row["transaction_id"].strip()
    if transaction_counts[transaction_id] > 1:
        issues.append("Repeated Transaction ID")

    #for Order_id
    if check_duplicate(row, duplicate_orders):
        issues.append("Possible duplicate transaction")


        
    

    if not cleaned_name:
        issues.append("Missing customer name")

    if cleaned_amount is None:
        issues.append("Invalid amount")
        cleaned_amount="Nill"

    if cleaned_date is None:
        issues.append("Invalid date")
        cleaned_date="Nill"

    if cleaned_status is None:
        issues.append("Invalid status")


    if len(issues) == 0:
        validity = "valid"
    else:
        validity = "invalid"    
   

    cleaned_row = {
        "transaction_id": row["transaction_id"],
        "original_customer_name": row["customer_name"],
        "customer_name": cleaned_name,
        "amount": cleaned_amount,
        "transaction_date": cleaned_date,
        "status": cleaned_status,
        "order_id": order_id,
        "validity":validity,
        'issues':"; ".join(issues) 
    }

    cleaned_rows.append(cleaned_row)





# Create cleaned.csv

with open("cleaned.csv", "w", newline="", encoding="utf-8") as file:
    fieldnames = [
        "transaction_id",
        "order_id",
        "original_customer_name",
        "customer_name",
        "amount",
        "transaction_date",
        "status",
        "validity",
        "issues"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    
    writer.writerows(cleaned_rows)

print("cleaned.csv created successfully!")



#Josn Report ------------------


#1)total inputs
input_rows = len(rows)


#2) Count valid and invalid rows
valid_rows = 0
invalid_rows = 0

for row in cleaned_rows:
    if row["validity"] == "valid":
        valid_rows += 1
    else:
        invalid_rows += 1



#3 duplicate counts
duplicate_count = 0
repeated_rows = 0
possible_duplicate = 0

for count in transaction_counts.values():
    if count > 1:
        duplicate_count += 1
        repeated_rows += count

for row in cleaned_rows:
    if "Possible duplicate transaction" in row["issues"]:
        possible_duplicate += 1
        




#4) Total revenue

total_revenue = 0

for row in cleaned_rows:

    if row["validity"] == "valid":

        amount = float(row["amount"])

        if row["status"] == "paid":
            total_revenue += amount

        elif row["status"] == "refund":
            total_revenue -= amount



#5) Create JSON report

report = {
    "input_rows": input_rows,
    "valid_rows": valid_rows,
    "invalid_rows": invalid_rows,
    "duplicate_count": duplicate_count,
    "possible_duplicate": possible_duplicate,
    "total_revenue": round(total_revenue, 2)
}


#6) Save report.json

with open("report.json", "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)

print("report.json created successfully!")