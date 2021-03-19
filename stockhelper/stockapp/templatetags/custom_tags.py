from django import template

register = template.Library()
# Add commas to long numbers to make them more readable
register.filter("commas", lambda num: f"{num:,}")
# Always show 2 decimal places for prices
register.filter("money", lambda num: f"{num:.2f}")
# Combine both filters above
register.filter("money_commas", lambda num: f"{num:,.2f}")
