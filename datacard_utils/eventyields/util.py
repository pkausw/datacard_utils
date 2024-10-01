from HiggsAnalysis.CombinedLimit.tool_base import rounding


def roundUnc(unc, method="Publication", prec=None):
    """By default, rounds uncertainty 'unc' according to the PDG rules plus one significant digit ("Publication").

    Optionally it rounds according with 'method':
        - "PDG" applies the PDG algorithm
        - "Publication" is like "PDG" with an extra significant digit (for results that need to be combined later)
        - "OneDigit" forces one single significant digit (useful when there are multiple uncertainties that vary by more than a factor 10 among themselves)

    Returns a tuple with (uncString, uncMagnitude), where magnitude is the power of 10 that applies to the string to recover the uncertainty.

    """

    # PDG rules (from the Introduction, Section 5.3)
    #
    # Uncertainty leading digits in range:
    #  100 to 354 -> keep 2 digits
    #  355 to 949 -> keep 1 digit
    #  950 to 999 -> keep 2 digits, rounding up to 1000 (e.g. 0.099 -> 0.10, not 0.1)

    uncDigs, uncMagnitude = rounding.getDigsMag(unc)

    # prec = 1
    unc3Digs = int(round(100 * uncDigs))

    if not prec:
        prec = 1
        if method == "SingleDigit":
            pass
        elif method == "PDG" or method == "Publication":
            if method == "Publication":
                prec += 1
            if 100 <= unc3Digs <= 354:
                prec += 1
        else:
            raise TypeError('Unknown precision method ("%s")' % method)
    else:
        prec = int(prec)
        # print(f"Using precision {prec}")
        

    uncStr = rounding.matchPrec(uncDigs, str(10 ** int(1 - prec)))

    # put String in integer form
    uncString = str((rounding.Decimal(uncStr) * (10 ** int(prec - 1))).quantize(rounding.Decimal("1")))
    uncMagnitude -= prec - 1

    return (uncString, uncMagnitude)


def PubRoundSym(val, unc):
    """Rounds a value with a single symmetric uncertainty according to the PDG rules and calculates the order of magnitude of both.

    Returns (valStr, [uncStr], uncMag)

    """

    assert unc > 0
    uncStr, uncMag = roundUnc(unc, prec=2)
    valStr = rounding.matchPrec(val / pow(10, uncMag), uncStr)
    return (valStr, [uncStr], uncMag)