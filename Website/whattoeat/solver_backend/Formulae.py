from whattoeat.solver_backend import UnitConversions, default_values

class FormulaeException(BaseException):
    def __init__(self,message):
        super(FormulaeException,self).__init__()
        self.message = message
    def __str__(self):
        return self.message

def validate_weight(value):
    try:
        value =  float(value)
    except ValueError:
        raise FormulaeException("Weight '" + value + "' not an acceptable value")
    return value

def validate_height(value):
    try:
        value =  float(value)
    except ValueError:
        raise FormulaeException("Height '" + value + "' not an acceptable value")
    return value

def convert_height_inches_to_metres(height):
    #let exception propogate if something goes wrong
    height = validate_height(height)

    height = UnitConversions.INCHES_TO_M * height
    return height


def convert_pounds_to_kg(weight):
    #let exception propogate if something goes wrong
    weight = validate_height(weight)

    weight = UnitConversions.POUNDS_TO_KILOS * weight
    return weight



def henry_oxford_bmr(height,weight,age,gender):
    '''
    Calculates BMR for an individual
    Gender can be 'm' or 'f'
    Height must be in metres
    Weight must be in kg
    Returned value rounded to 1 decimal place
    '''
    calPerDay = 0
    if age <= 0 or height <= 0 or  weight <= 0 or gender not in ['m','f'] :
            raise FormulaeException("User details are invalid")
        
    if gender == 'm':
        if age >= 0 and age < 3 :
            calPerDay = (28.2 * weight) + (895 * height) - 371
        elif age >= 3 and age < 10 :
            calPerDay = (15.1 * weight) + (74.2 * height) + 306
        elif age >= 10 and age < 18:
            calPerDay = (15.6 * weight) + (266 * height) + 299
        elif age >= 18 and age < 30:
            calPerDay = (14.4 * weight) + (313 * height) + 113
        elif age >= 30 and age < 60:
            calPerDay = (11.4 * weight) + (541 * height) - 137
        elif age >= 60:
            calPerDay = (11.4 * weight) + (541 * height) - 256
    elif gender == 'f':
        if age >= 0 and age < 3:
            calPerDay = (30.4 * weight) + (703 * height) - 287
        elif age >= 3 and age < 10 :
            calPerDay = (15.9 * weight) + (210 * height) + 349
        elif age >= 10 and age < 18:
            calPerDay = (9.4 * weight) + (249 * height) + 462
        elif age >= 18 and age < 30:
            calPerDay = (10.4 * weight) + (615 * height) - 282
        elif age >= 30 and age < 60:
            calPerDay = (8.18 * weight) + (502 * height) - 11.6
        elif age >= 60:
            calPerDay = (8.52 * weight) + (421 * height) + 10.7

    return round(calPerDay,1)

def PAL_lookup(age):
    age = int(age)
    if age < 0 :
        raise FormulaeException("Age cannot be negative")
    elif age>= 0 and age < 3 :
        return 1.4
    elif age >= 3 and age < 10:
        return 1.58
    elif age >= 10 and age < 18:
        return 1.75
    elif age >= 18:
        return 1.63

def correct_for_goal(goal):
    if goal == 'lose weight':
        return -500
    elif goal == 'gain weight':
        return 200
    else:
        return 0


def calculate_calories_per_day(height,weight,age,gender,goal):
    BMR = henry_oxford_bmr(height,weight,age,gender)
    PAL = PAL_lookup(age)
    correction_for_goal = correct_for_goal(goal)
    return (BMR * PAL) + correction_for_goal

def daily_protein(calories_per_day,ratio = default_values.RATIO_CALORIES_PROTEIN):
    return (calories_per_day * ratio) / default_values.CALORIES_PER_GRAM_PROTEIN

def daily_carbs(calories_per_day,ratio = default_values.RATIO_CALORIES_CARBS):
    return (calories_per_day * ratio) / default_values.CALORIES_PER_GRAM_CARBS

def daily_fat(calories_per_day, ratio = default_values.RATIO_CALORIES_FAT):
    return (calories_per_day * ratio) /default_values.CALORIES_PER_GRAM_FAT

def daily_sugar(calories_per_day,ratio = default_values.RATIO_CALORIES_SUGAR):
    return (calories_per_day * ratio) / default_values.CALORIES_PER_GRAM_CARBS

def daily_satfat(calories_per_day,ratio = default_values.RATIO_CALORIES_SATFAT):
    return (calories_per_day * ratio) / default_values.CALORIES_PER_GRAM_FAT

def default_daily_protein_ratio():
    return default_values.RATIO_CALORIES_PROTEIN

def default_daily_carbs_ratio():
    return default_values.RATIO_CALORIES_CARBS

def default_daily_fat_ratio():
    return default_values.RATIO_CALORIES_FAT

def default_max_salt_grams():
    return default_values.SALT_LIMIT_GRAMS

def default_min_fibre_grams():
    return default_values.FIBRE_MINIMUM_GRAMS

def default_error_margin():
    return default_values.DEFAULT_ERROR_MARGIN

def BMI(height, weight):
    return weight / (height * height)


#main()
