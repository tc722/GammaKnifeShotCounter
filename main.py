import psycopg2
from psycopg2 import OperationalError
import sys  
import configparser
from tabulate import tabulate

config = configparser.ConfigParser()
config.read('config.ini')

db_name = config['Database']['name']
db_host = config["Database"]['host']
db_user = config['Database']['user']
db_password = config["Database"]['password']
db_port = config["Database"]['port']

print("Attempting to connect to the GammaKnife database...")

try:
    conn = psycopg2.connect(database=db_name, 
                            host=db_host,
                            user=db_user,
                            password=db_password,
                            port=db_port,
                            connect_timeout=3
                            )
    print("Successfully connected!")
except OperationalError as e:
    print("\n" + "-"*60)
    print("ERROR: Could not connect to the database.")
    print("-"*60)
    print("Please check the parameters in the config.ini file.")
    print(f"\nTechnical Error Message: {e}")
    sys.exit()


cursor = conn.cursor()
cursor.execute("select patients.first_name,patients.last_name,patients.id,examinations.diagnosis_name,treatment_plans.\"name\",treatment_plans.treatment_date "
                "from public.patients,public.examinations,public.treatment_plans "
                "where treatment_plans.root_uid = examinations.uid AND examinations.parent_uid = patients.uid and treatment_plans.state = 5 "
                "order by treatment_plans.treatment_date desc ")

patientList = cursor.fetchmany(size=5)

headers = ["Index", "First Name", "Last Name", "MRN", "Diagnosis", "Plan Name", "Treatment Date"]
table_data = []
for i, row in enumerate(patientList, start=1):

    table_data.append([i] + list(row))
    
print("The most recent five patients are:\n")

print(tabulate(table_data, headers=headers, tablefmt="grid"))

max_index = len(patientList)

while True:
    # Ask for input
    user_input = input(f"Please enter the index number of plan (1-{max_index}): ")

    # Check 1: Did they enter a number?
    if not user_input.isdigit():
        print("Error: Please enter a valid number.")
        continue # Skip the rest and ask again

    # Convert to integer
    selected_index = int(user_input)

    # Check 2: Is the number within the valid range?
    if 1 <= selected_index <= max_index:
        break # The input is good! Exit the loop.
    else:
        print(f"Error: Number must be between 1 and {max_index}.")

selected_patient = patientList[selected_index - 1]

ptFirstName = selected_patient[0]
ptLastName  = selected_patient[1]
ptPlanName  = selected_patient[4]
ptPlanDate  = selected_patient[5].strftime("%Y-%m-%d")

print(f"Retrieve data for {ptFirstName} {ptLastName}")

sql2 = ("select concat(shots.c_sector_1,shots.c_sector_2,shots.c_sector_3,shots.c_sector_4,shots.c_sector_5,shots.c_sector_6,shots.c_sector_7,shots.c_sector_8) as pattern "
        "from  public.patients, public.examinations, public.treatment_plans, public.targets, public.shots "
        "where "
        "patients.first_name = \'" + ptFirstName + "\' "
        "and patients.last_name = \'" + ptLastName + "\' "
        "and treatment_plans.\"name\" = \'" + ptPlanName + "\' "
        "and treatment_plans.treatment_date = \'" + ptPlanDate + "\' "
        "and treatment_plans.root_uid = examinations.uid "
	    "and examinations.parent_uid = patients.uid "
	    "and shots.root_uid = examinations.uid "
	    "and targets.root_uid = examinations.uid "
	    "and shots.parent_uid = targets.uid "
	    "and targets.parent_uid = treatment_plans.uid "
	    "and treatment_plans.state = 5")

cursor.execute(sql2)
shotList = cursor.fetchall()


shotListX = [item.replace("16","7") for t in shotList for item in t]
print(shotListX)
# initiate a null set
uniqueShots = []

# loop over all shots
for shot in shotListX:
    shotList = []
    shotList[:0] = shot
    isShotUnique = True
    for angle in range(8):
        shotListRot = "".join(shotList[-angle:] + shotList[:-angle])
        if shotListRot in uniqueShots:
            isShotUnique = False
    if isShotUnique:
        uniqueShots.append(shot)

index = 1
for row in uniqueShots:
    print(index, "\t", row)
    index = index+1

print(f"There are {len(shotListX)} shots and {len(uniqueShots)} unique shot patterns used in the plan.")

cursor.closed


