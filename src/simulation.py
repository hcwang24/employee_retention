import numpy as np
import pandas as pd
import random
from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)

# Seed for reproducibility
np.random.seed(42)

# Number of employees
n_employees = np.random.randint(1000, 2000)

# Create columns
departments = ['Engineering', 'Sales', 'HR', 'Marketing', 'Finance', 'Operations', 'IT']
job_levels = ['L1', 'L2', 'L3', 'L4', 'L5'] # Lower level 1, higher level 5
performance_ratings =  [1, 2, 3, 4, 5] # Lower is worse, higher is better
reasons_for_leaving = ['Work-Life Balance', 'Compensation', 'Career Growth', 'Personal Reasons', 'Retirement']
genders = ['Male', 'Female', 'Non-binary']
age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65']

# Simulate data
data = {
    'Employee_ID': [i for i in range(1, n_employees+1)],
    'Gender': [random.choices(genders, weights=[0.49, 0.49, 0.02], k=1)[0] for _ in range(n_employees)], 
    'Department': [random.choices(departments, weights=[0.3, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1], k=1)[0] for _ in range(n_employees)],
    'Job_Level': [random.choice(job_levels) for _ in range(n_employees)],
    'Performance_Rating': [random.choice(performance_ratings) for _ in range(n_employees)],
    'Satisfaction_Score': (np.random.normal(7, 2, n_employees)) // 1,  # Satisfaction score will be 5-10 range for most
    'Work_Hours': (np.random.normal(40, 5, n_employees) // 5) * 5,  # Most employees work 35-45 hours a week
    'Start_Date': [fake.date_between(start_date='-15y', end_date='-1y') for _ in range(n_employees)],
    'Reason_for_Leaving': [random.choice(reasons_for_leaving) if random.random() < 0.25 else None for _ in range(n_employees)],
}

# Generate End_Date based on Start_Date
data['End_Date'] = []
data['Reason_for_Leaving'] = []

today_date = pd.Timestamp.today()

for start_date in data['Start_Date']:
    if random.random() < 0.30:  # 30% chance of having an End_Date
        # Add a random number of days (1 to 365) to Start_Date
        days_to_add = random.randint(1, 1000)
        end_date = start_date + pd.Timedelta(days=days_to_add)
        if end_date <= today_date.date():
            data['End_Date'].append(end_date)
        else:
            data['End_Date'].append(today_date)
        data['Reason_for_Leaving'].append(random.choice(reasons_for_leaving))
    else:
        data['End_Date'].append(None)
        data['Reason_for_Leaving'].append(None)


# Convert to DataFrame
employee_data = pd.DataFrame(data)

employee_data['Age_Group'] = [random.choice(age_groups) for _ in range(n_employees)]

# Engineers - Worse WLB, Lower Satisfaction, More Turnover
is_engineer = employee_data['Department'] == 'Engineering'
employee_data.loc[is_engineer, 'Satisfaction_Score'] = (np.random.normal(5, 1.5, is_engineer.sum())) // 1  # Engineers' satisfaction is lower
employee_data.loc[is_engineer, 'Work_Hours'] = (np.random.normal(50, 5, is_engineer.sum())) // 1  # Engineers work longer hours
employee_data.loc[is_engineer, 'Reason_for_Leaving'] = employee_data.loc[is_engineer, 'Reason_for_Leaving'].apply(
    lambda x: 'Work-Life Balance' if pd.notna(x) else None
)

# Non-engineers by department - Assign reasons for leaving based on common trends for each department
# Sales: Leave for compensation
is_sales = employee_data['Department'] == 'Sales'
employee_data.loc[is_sales & employee_data['End_Date'].notna(), 'Reason_for_Leaving'] = 'Compensation'

# HR and Finance: Leave for career growth
is_hr_finance = employee_data['Department'].isin(['HR', 'Finance'])
employee_data.loc[is_hr_finance & employee_data['End_Date'].notna(), 'Reason_for_Leaving'] = 'Career Growth'

# Marketing: Leave for personal reasons or retirement
is_marketing = employee_data['Department'] == 'Marketing'
employee_data.loc[is_marketing & employee_data['End_Date'].notna(), 'Reason_for_Leaving'] = employee_data.loc[is_marketing & employee_data['End_Date'].notna(), 'Reason_for_Leaving'].apply(
    lambda x: random.choice(['Personal Reasons', 'Retirement']) if pd.notna(x) else None
)

# Operations and IT: Mix of reasons (balanced between compensation, career growth, etc.)
is_ops_it = employee_data['Department'].isin(['Operations', 'IT'])
employee_data.loc[is_ops_it & employee_data['End_Date'].notna(), 'Reason_for_Leaving'] = employee_data.loc[is_ops_it & employee_data['End_Date'].notna(), 'Reason_for_Leaving'].apply(
    lambda x: random.choice(reasons_for_leaving) if pd.notna(x) else None
)

# Clip Satisfaction_Score and Work_Hours to realistic bounds
employee_data['Satisfaction_Score'] = employee_data['Satisfaction_Score'].clip(1, 10)
employee_data['Work_Hours'] = employee_data['Work_Hours'].clip(30, 70)

# Add duration at the company
employee_data['Duration_in_Company'] = (pd.to_datetime('today') - pd.to_datetime(employee_data['Start_Date'])).dt.days

# View the adjusted dataset
employee_data.head()

# Save to CSV
employee_data.to_csv("../data/employee.csv", index=False)