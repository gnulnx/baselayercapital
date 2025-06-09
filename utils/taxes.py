STATE = 0.05


def monthly_federal_tax(income_monthly):
    annual = income_monthly * 12
    brackets = [0, 23200, 94300, 201050, 383900, 487450, 731200, float("inf")]
    rates = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    tax = 0
    for i in range(len(rates)):
        low, high = brackets[i], brackets[i + 1]
        if annual > low:
            taxable = min(annual, high) - low
            tax += taxable * rates[i]
        else:
            break
    return tax / 12
