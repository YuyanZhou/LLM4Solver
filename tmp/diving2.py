
import math

def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    if not mayrounddown and not mayroundup:
        score = -1e10  # Penalize variables that cannot be rounded
        roundup = False
    else:
        roundup = candsfrac > 0.5
        
        # Calculate potential objective improvement
        obj_diff_down = obj * (rootsolval - candsol) + pscostdown
        obj_diff_up = obj * (1 - candsol) + pscostup
        obj_improvement = max(0, obj_diff_up, obj_diff_down) / (objnorm + 1e-9)
        
        # Calculate exploration and diversification scores
        exploration_score = abs(candsfrac - 0.5) * (1 + nNonz * isBinary)
        diversification_score = 1 / (nlocksdown + nlocksup + 1e-9)
        
        # Combine scores with objective coefficient
        if roundup:
            score = obj * (exploration_score + obj_improvement * diversification_score - nlocksup)
        else:
            score = obj * (exploration_score + obj_improvement * diversification_score - nlocksdown)
    
    return score, roundup
