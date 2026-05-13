
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    # Determine rounding direction based on the fractional value
    roundup = candsfrac >= 0.5
    
    # Calculate score based on provided features with penalties and prioritization
    score = (1 / (1 + abs(candsfrac - 0.5))) * (1 / (1 + candsol)) * (1 / (1 + obj)) * (1 / (1 + objnorm)) * (1 / (1 + max(pscostdown, pscostup))) * (1 / (1 + abs(nlocksdown - nlocksup))) * (1 / (1 + nNonz)) * (1 / (1 + rootsolval))
    
    # Penalize rounding feasibility for exploration, promote exploration for binary variables, additional adjustments for rounding directions
    if mayrounddown:
        score *= 0.85
        if not roundup:
            score *= 1.1  # Adjust penalty if rounding down is preferred
    if mayroundup:
        score *= 0.85
        if roundup:
            score *= 1.1  # Adjust penalty if rounding up is preferred
    if isBinary:
        score *= 1.15
    if nNonz > 5:  # Penalize variables with a high number of nonzero entries
        score *= 0.90
        
    return score, roundup
