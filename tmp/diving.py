
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Initialize the score
    score = 0.0
    roundup = False
    
    # Penalize variables with limited rounding options
    if not mayrounddown or not mayroundup:
        score -= 1000
    
    # Prioritize variables with a significant fractional part
    score += candsfrac
    
    # Consider the variable's impact on the objective function
    score += obj + objnorm
    
    # Incorporate historical data from previous relaxations
    if rootsolval != 0.0:
        score += rootsolval
    
    # Determine rounding direction based on the variable's properties
    if pscostup > pscostdown:
        roundup = True
    
    return score, roundup
