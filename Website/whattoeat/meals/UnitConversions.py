INCHES_TO_M = 0.0254 # 1 inch = 0.0254 m
POUNDS_TO_KILOS = 0.453592
OZ_TO_G = 28.3495

def roundToDecimalPlaces(val,noPlaces):
    val = int(val * (10**noPlaces))
    val = float(val) / (10**noPlaces)
    return val

