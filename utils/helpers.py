from num2words import num2words
import datetime

def amount_in_words(amount):
    return num2words(amount, lang='en_IN').title()

def current_date():
    return datetime.datetime.now().isoformat()

def calculate_deductions(payable, income_tax_percent, deposit_percent, cess_percent):
    income_tax = round(payable * (income_tax_percent / 100), 0)
    deposit = round(payable * (deposit_percent / 100), 0)
    cess = round(payable * (cess_percent / 100), 0)
    total_deduction = income_tax + deposit + cess
    net_amount = payable - total_deduction
    return income_tax, deposit, cess, total_deduction, net_amount
