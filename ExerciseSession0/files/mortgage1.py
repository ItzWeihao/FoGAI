MONTHS_IN_YEAR = 12

principal = 500000.0
rate = 0.05
payment = 2684.11
total_paid = 0.0


months = 1
while principal > 0:
    extra_payment = 1000 if months <= 12 else 0
    principal = principal * (1 + rate / MONTHS_IN_YEAR) - payment - extra_payment
    total_paid = total_paid + payment + extra_payment
    months += 1

print("Total paid", total_paid)
