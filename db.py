import psycopg2
from PyPDF2 import PdfReader

# === 1. Parse PDF ===
reader = PdfReader("rwservlet (4).pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()

# === 2. Dummy parse — replace with real regex/parsing ===
insured_name = "EUROBIZ CORPORATION"
address = "170-CCA, PHASE-VI, DHA, LAHORE"
vehicle_make = "Model"
vehicle_model = "2025"
vehicle_reg = "N.A"
horse_power = 2755
chassis_no = "GUN156R-1106989"
engine_no = "IGD5774029"
speedometer = 0
colour = "STELLAR WHITE"
estimated_market_value = 18093000
is_owner = True
is_hire_purchase = False
last_insured_with = None
declaration = "I/WE desire to insure..."
signature_name = "SHAHID.RASHEED"
branch = "UNITED INSURANCE CO. OF PAKISTAN LTD."
remarks = "Complete Survey"

# === 3. Insert into PostgreSQL ===
conn = psycopg2.connect(
    dbname="Surveyor",
    user="postgres",
    password="United2025",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
cur.execute("""
    INSERT INTO vehicle_inspection (
        insured_name, address, vehicle_make, vehicle_model, vehicle_reg,
        horse_power, chassis_no, engine_no, speedometer, colour,
        estimated_market_value, is_owner, is_hire_purchase,
        last_insured_with, declaration, signature_name, branch, remarks
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
    insured_name, address, vehicle_make, vehicle_model, vehicle_reg,
    horse_power, chassis_no, engine_no, speedometer, colour,
    estimated_market_value, is_owner, is_hire_purchase,
    last_insured_with, declaration, signature_name, branch, remarks
))

conn.commit()
cur.close()
conn.close()

print("✅ Inserted into database!")
