MONTHS_IN_YEAR = 12

principal = 500000.0
rate = 0.05
payment = 2684.11
total_paid = 0.0

while principal > 0:
    principal = principal * (1 + rate / MONTHS_IN_YEAR) - payment
    total_paid = total_paid + payment

print("Total paid", total_paid)
