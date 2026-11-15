"""Shared civil-year arithmetic; scientific BP uses the fixed 1950 CE epoch."""
def civil(ordinal):
    return ordinal if ordinal > 0 else ordinal - 1

def bp_to_civil(years_before_present):
    return civil(1950 - years_before_present)
