
def myheurdiving(mayrounddown, mayroundup, candsfrac, candsol, nlocksdown, nlocksup, obj, objnorm, pscostdown, pscostup, rootsolval, nNonz, isBinary):
    
    score = candsfrac * (1 + nlocksdown + nlocksup) / (1 + pscostdown + pscostup) / (1 + nNonz) * objnorm / max(1, rootsolval)
    
    roundup = True if candsfrac >= 0.5 or (mayroundup and not mayrounddown) else False
    
    return score, roundup
