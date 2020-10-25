# Budget Calculator
Inspired by Dave Ramsey's 7 Baby Steps

## Installation
pip install these packages:
python==3.8
numpy==1.19.2
pandas==1.1.3
xlrd==1.2.0

## How to use this Calculator
1. Create new sheet at the end of the queue and give it a unique name.
2. Input monthly spending and loan information.
  - Tag loans as type "Loan". All fields for loans are required. Non-loans must
be left blank.
  - Tag expenses as type "Expenses". Leave loan columns blank.
  - Tag income as type "Income"
  - Tag any amount in to be calculated from bank assets as type "Bank"
3. Run the budget.py file
4. View the "report.txt" file for budget metrics and recommended allocations.

## Deeper Analysis
- The data/Transactions.csv file can be explored after several months of budgeting
for deeper exploration.
- All other files in the data folder are loan matrices with all minimum
payments calculated for the entire life of the loan.
- The budget.db file is an sqlite database that holds all tables, matrices,
and transactions for the life of the budget calculator.  

```
.
├── budget.db # database where all transactions and tables are stored.
├── budget.py # Main program that calculates budgets.
├── budget.xlsx # Main user input file.
├── data
│   ├── ClimbCredit.csv
│   ├── Mortgage.csv
│   ├── MyGreatLakes.csv
│   ├── Subaru.csv
│   ├── Toyota.csv
│   └── Transactions.csv # All transactions that have occurred during from
running the budget.py file.
├── docs
├── library.py # Class and functions library.
├── __pycache__
│   ├── library.cpython-37.pyc
│   └── library.cpython-38.pyc
├── readme.md
├── report.txt # Simple output file.
└── tree.txt

3 directories, 15 files
```
