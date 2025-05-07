from num2words import num2words
import datetime

def amount_in_words(amount):
    return num2words(amount, lang='en_IN').title()

def current_date():
    return datetime.datetime.now().isoformat()

def calculate_deductions(payable, income_tax_percent, deposit_percent, cess_percent, restricted_to_amount, scheme, cgst_percent, sgst_percent):
    # Determine the base amount for all tax calculations
    calculation_base_for_taxes = restricted_to_amount
    is_jjm_scheme = scheme and scheme.upper() == "JJM"

    if is_jjm_scheme:
        calculation_base_for_taxes = (restricted_to_amount * 100) / 118
    
    income_tax = round(calculation_base_for_taxes * (income_tax_percent / 100), 0)
    deposit = round(calculation_base_for_taxes * (deposit_percent / 100), 0)
    cess = round(calculation_base_for_taxes * (cess_percent / 100), 0)
    cgst_amount = round(calculation_base_for_taxes * (cgst_percent / 100), 0)
    sgst_amount = round(calculation_base_for_taxes * (sgst_percent / 100), 0)

    # This is the sum of all calculated tax components
    total_deduction_for_record = income_tax + deposit + cess + cgst_amount + sgst_amount

    # Calculate net_amount based on the specific logic provided
    if is_jjm_scheme:
        net_amount = restricted_to_amount - total_deduction_for_record
    else: # Not JJM scheme
        net_amount = restricted_to_amount - income_tax - deposit
        # Note: For non-JJM, cess, cgst, sgst are calculated and will be part of total_deduction_for_record,
        # but are not subtracted for this specific net_amount calculation as per user feedback.
        
    return income_tax, deposit, cess, cgst_amount, sgst_amount, total_deduction_for_record, net_amount
