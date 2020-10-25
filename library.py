import pandas as pd


def allocate(to_val, from_val, amount):
    """
    Allocates the amount to and from two int or float type variables.
    """
    from_val -= amount
    to_val += amount

    return to_val, from_val, amount

def calculate_payment(balance, rate, num_payments):
    """
    Calculates a loan's monthly payment.
    """
    return balance*(rate/12)*((1+(rate/12))**num_payments)/(((1+(rate/12))**num_payments)-1)

class Loan:
    def __init__(self, balance, payment, rate, num_payments, extras=0):

        """
        Stores several features about a loan.
        """
        self.balance = balance
        self.rate = rate
        self.num_payments = num_payments
        self.extras = extras
        self.payment = payment+extras
        self.interest = balance*(rate/12)
        self.repayment = payment-self.interest


def calculate_loan_matrix(balance, rate, num_payments, extras=0):
    """
    Calculates the loan matrix and outputs as a pandas dataframe.
    """
    payment = calculate_payment(balance, rate, num_payments)
    loan = Loan(balance, payment, rate, num_payments, extras=extras)

    dict_table = {'Balance':[], 'Payment':[], 'Interest':[], 'Repayment':[]}
    for num in range(num_payments):
        dict_table['Balance'].append(round(loan.balance-loan.repayment, 2))
        dict_table['Payment'].append(round(payment, 2))
        dict_table['Interest'].append(round(loan.interest, 2))
        dict_table['Repayment'].append(round(loan.repayment, 2))
        loan = Loan(loan.balance-loan.repayment, payment, rate, num_payments-1)

    return pd.DataFrame(dict_table)
############# library
