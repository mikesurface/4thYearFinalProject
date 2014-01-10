from whattoeat.meals import UnitConversions, default_values


def validate_height_weight(value):
    try:
        value =  float(value)
    except TypeError:
        raise Exception()
        return
    return value

def convert_height_inches_to_metres(height):
    try:
        height = validate_height_weight(height)
    except Exception:
        print "Height could not be converted from imperial to metric"

    height = UnitConversions.INCHES_TO_M * height
    return height


def convert_pounds_to_kg(weight):
    try:
        weight = validate_height_weight(weight)
    except Exception:
        print "Weight could not be converted from imperial to metric"

    weight = UnitConversions.POUNDS_TO_KILOS * weight
    return weight



def henry_oxford_bmr(height,weight,age,gender):
    calPerDay = 0
    if age <= 0 or height <= 0 or  weight <= 0 or gender not in ['m','f'] :
            raise Exception("User details are invalid")
        
    if gender == 'm':
        if age >= 0 and age < 3 :
            calPerDay = (28.2 * weight) + (895 * height) - 371
        elif age >= 3 and age < 10 :
            calPerDay = (15.1 * weight) + (72.4 * height) + 306
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

    return calPerDay

def PAL_lookup(age):
    if age < 0 :
        raise Exception("Age cannot be negative")
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

def main():
    age = 20
    height = 71
    weight = 185
    gender = 'm'
    goal = 'maintain weight'

    height = convert_height_inches_to_metres(height)
    print "HEIGHT: " + str(height)

    weight = convert_pounds_to_kg(weight)
    print "WEIGHT: " + str(weight)

    calPerDay = henry_oxford_bmr(age = 20, height = height, weight = weight, gender = 0)
    print "BMR: " + str(calPerDay)

    PAL = PAL_lookup(age)
    print "PAL: " + str(PAL)

    daily_kcal = calculate_calories_per_day(height,weight,age,gender,goal)
    print "KCAL per day: " + str(daily_kcal)

    protein_day = daily_protein(daily_kcal)
    carbs_day = daily_carbs(daily_kcal)
    fat_day = daily_fat(daily_kcal)
    print "PER DAY PROTEIN: " + str(protein_day) + "g CARBS: " + str(carbs_day) + "g FAT: " + str(fat_day) +  "g"

    bmi = BMI(height, weight)
    print "BMI :" + str(bmi)

#main()
