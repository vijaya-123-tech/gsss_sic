# tax_level5.py

import tax_level1 as t1
import tax_level2 as t2
import tax_level3 as t3
import tax_level4 as t4

def generate_report():
    print("=" * 40)
    print("        Employee Tax Report 2023-24")
    print("=" * 40)
    print(f"Employee Name        : {t1.name}")
    print(f"Employee ID          : {t1.id}")
    print("-" * 40)
    print(f"Gross Monthly Salary : ₹{t1.gross_monthly_salary:,.2f}")
    print(f"Annual Gross Salary  : ₹{t1.gross_annual_salary:,.2f}")
    print(f"Standard Deduction   : ₹50,000.00")
    print(f"Taxable Income       : ₹{t2.taxable_income:,.2f}")
    print("-" * 40)
    print("Tax Breakdown (New Regime 2023):")
    print("  ₹0 - ₹3,00,000      : 0%")
    print("  ₹3,00,001 - ₹6,00,000 : 5%")
    print("  ₹6,00,001 - ₹9,00,000 : 10%")
    print("  ₹9,00,001 - ₹12,00,000: 15%")
    print("  ₹12,00,001 - ₹15,00,000: 20%")
    print("  Above ₹15,00,000      : 30%")
    print(f"Cess Amount          : ₹{t3.cess_amount:,.2f}")
    
    # Check rebate
    if t2.taxable_income <= 7_00_000:
        total_tax = 0
    else:
        total_tax = t3.total_tax_amount
    
    print(f"Total Tax Payable    : ₹{total_tax:,.2f}")
    print("-" * 40)
    print(f"Net Annual Salary    : ₹{t4.net_annual_salary:,.2f}")
    print("=" * 40)

if __name__ == "__main__":
    generate_report()
