# __Environment__
import numpy as np
import pandas as pd
import sqlite3 as sql
from datetime import datetime
from library import *

cd_data = 'data/'
to_ret = 0
# load in the furthest right sheet as a pandas dataframe.
sheet_name = pd.ExcelFile('budget.xlsx').sheet_names[-1]
df = pd.read_excel('budget.xlsx', sheet_name=sheet_name)


# Read in and populate database.
with sql.connect('budget.db') as con:
    df.to_sql(sheet_name, con, if_exists='replace')

df_bank = pd.read_sql_query("""
SELECT *
FROM {0}
WHERE Type == 'Bank';
""".format(sheet_name), con)

# __SQL Queries__
df_expenses = pd.read_sql_query("""
SELECT *
FROM {0}
WHERE Type == 'Loan'
OR Type == 'Insurance'
OR Type == 'Service'
OR Type == 'Expense'
AND Active == True
""".format(sheet_name), con)

df_income = pd.read_sql_query("""
SELECT *
FROM {0}
WHERE Type == 'Income'
AND Active == True
""".format(sheet_name), con)

df_debt = pd.read_sql_query("""
SELECT *
FROM {0}
WHERE Type == 'Loan'
AND Active == True
""".format(sheet_name), con)

df_retirement = pd.read_sql_query("""
SELECT *
FROM {0}
WHERE Type == 'Retirement'
AND Active == True
""".format(sheet_name), con)

# Allocate payments to loans
# for expense in df_expenses.index:


bank = df_bank['Value'].sum()
expenses = df_expenses['Value'].sum()
income = df_income['Value'].sum()
debt = df_debt['Loan'].sum()
budget = income-expenses
retirement = df_retirement['Value'].sum()

# Write matrix to database.

ls_interest = []
ls_repayment = []
for row in df_debt.iterrows():
    loan = row[1][4] # Loan
    rate = row[1][8] # Rate
    num_payments = int(row[1][6]) # PaymentsLeft
    current_payment = int(row[1][5]) # Payments
    payment = calculate_payment(loan, rate, num_payments)
    loan_matrix = calculate_loan_matrix(loan, rate, num_payments, extras=loan-payment)
    label = str(row[1][1]).title().replace(' ', '') # Label
    loan_matrix.to_sql(label, con, if_exists='replace')
    loan_matrix.to_csv(cd_data+label+'.csv', index=False)
    ls_interest.append(float(loan_matrix['Interest'].values[current_payment]))
    ls_repayment.append(float(loan_matrix['Repayment'].values[current_payment]))

interest = sum(ls_interest)
repayment = sum(ls_repayment)



assert budget > 0, """The budget is {0} after expenses. Unable to allocate
enough funds for monthly minimum expenses.""".format(budget)


# Step 1: $1000 emergency fund in bank
to_ef = 0
if bank < 1000:
    if bank-budget <= budget:
        bank, budget, to_ef = allocate(bank, budget, bank-budget)

    elif bank-budget > budget:
        bank, budget, to_ef = allocate(bank, budget, budget)

# Step 2: Pay off all debt except mortgage. ( Debt Snowball )
to_debt = 0
if debt-df_debt['Loan'].max() > 0:
    if (debt-df_debt['Loan'].max())-budget <= budget:
        debt, budget, to_debt = allocate(debt, budget, (debt-df_debt['Loan'].max())-budget)
    elif (debt-df_debt['Loan'].max())-budget > budget:
        debt, budget, to_debt = allocate(debt, budget, budget)

# Step 3: 6-month emergency fund.
if (expenses*6)-bank > 0:
    if (expenses*6)-bank >= budget:
        bank, budget, to_ef = allocate(bank, budget, budget)
    elif (expenses*6)-bank < budget:
        bank, budget, to_ef = allocate(bank, budget, (expenses*6)-bank)

# Step 4: Pay off mortgage.
if (debt > 0) and (to_debt == 0):
    if debt-budget <= budget:
        debt, budget, to_debt = allocate(debt, budget, debt-budget)
    elif debt-budget > budget:
        debt, budget, to_debt = allocate(debt, budget, budget)

else:
    retirement, budget, to_ret = allocate(budget, retirement, budget*0.15)

current_time = datetime.now()
dict_allocated = {
'Bank': [bank],
'Income': [income],
'Expenses': [expenses],
'Debt': [debt],
'InterestPaid': [interest],
'RepaymentsPaid': [repayment],
'LeftoverBudget': [budget],
'ToEmergencyFund': [to_ef],
'ToDebt': [to_debt],
'ToRetirement': [to_ret],
'RecordTime': [current_time.strftime("%m-%Y")]
}



df_allocated = pd.DataFrame(dict_allocated)

# Write to database
df_allocated.to_sql('Transactions', con, if_exists='append')

# Gather all unique transactions
df_transactions = pd.read_sql_query("""
SELECT DISTINCT *
FROM Transactions
""", con)

df_transactions.to_csv(cd_data+'Transactions.csv', index=False)
df_transactions
df_metrics = pd.read_sql_query("""
SELECT DISTINCT SUM(InterestPaid) as TotalInterest,
SUM(RepaymentsPaid) as TotalRepayments
FROM Transactions
""", con)

dict_metrics = df_metrics.to_dict()
dict_metrics
# Write report
report = ('-------' + str(dict_allocated['RecordTime'][0]) + ' FINANCIAL REPORT--------' +
'\n--------------ASSETS-------------------' +
'\nIncome: ' + str(round(dict_allocated['Income'][0], 2)) +
'\nBank: ' + str(round(dict_allocated['Bank'][0], 2)) +
'\n---------------MONTHLY EXPENSE---------' +
'\nExpenses: ' + str(round(dict_allocated['Expenses'][0], 2)) +
'\n----------------DEBT-------------------' +
'\nDebt: ' + str(round(dict_allocated['Debt'][0], 2)) +
'\nInterest: ' + str(round(dict_allocated['InterestPaid'][0], 2)) +
'\nTotal Interest Paid: ' + str(round(dict_metrics['TotalInterest'][0], 2)) +
'\nRepayment: ' + str(round(dict_allocated['RepaymentsPaid'][0], 2)) +
'\nTotal Repayment Paid: ' + str(round(dict_metrics['TotalRepayments'][0], 2)) +
'\n-----------------ALLOCATIONS-----------' +
'\nTo Emergency Fund: ' + str(round(dict_allocated['ToEmergencyFund'][0], 2)) +
'\nTo Debt: ' + str(round(dict_allocated['ToDebt'][0], 2)) +
'\nTo Retirement: ' + str(round(dict_allocated['ToRetirement'][0], 2)) +
'\nLeftover Budget: ' + str(round(dict_allocated['LeftoverBudget'][0], 2)))

with open('report.txt', 'w+') as file:
    file.write(report)
