MONTHS_IN_YEAR = 12

principal = 500000.0
rate = 0.05
payment = 2684.11
total_paid = 0.0

extra_payment_start_month = 5 * 12 + 1  # 61
extra_payment_end_month = 9 * 12  # 108
extra_payment = 1000

months = 1
while principal > 0:
    current_extra_payment = (
        extra_payment
        if months > extra_payment_start_month and months < extra_payment_end_month
        else 0
    )
    principal = (
        principal * (1 + rate / MONTHS_IN_YEAR) - payment - current_extra_payment
    )
    total_paid = total_paid + payment + current_extra_payment
    months += 1

print("Total paid", total_paid)
