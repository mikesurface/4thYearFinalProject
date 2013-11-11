from MealClasses import *
from Numberjack import *
from Mistral import Solver
import math

SCALING_FACTOR = 1000;

def compute_nutrient_bounds(requirements,uppervalues,lowervalues):
    requirements = requirements.to_array()
    for i in range(0,8):
        requirement = requirements[i]
        if requirement == None: #null catch
            continue
        margin_percentage = requirement.error_margin
        margin = requirement.val * (margin_percentage / 100.0)
        uppervalues.append(int(math.floor((requirement.val + margin) *SCALING_FACTOR)))
        lowervalues.append(int(math.ceil((requirement.val - margin) *SCALING_FACTOR)))

        
def generate_meal(requirements,ingredients):
    upperbounds = []
    lowerbounds = []
    compute_nutrient_bounds(requirements,upperbounds,lowerbounds)
    print upperbounds
    print lowerbounds

    numIngredients = len(ingredients)           #number of nutrients being considered
    
    #extract required nutritional content
    

    minCal = ingredients[0].cal;
    #value of calories in least calorific ingredient
    #used to set max quantity of ingredients
    #as the quantity of any ingredient cannot exceed
    #the upper bound on calories divided by the 
    #lowest calorific value
    
    for ingredient in ingredients:
        calories.append(int(ingredient.cal * SCALING_FACTOR))
        prot.append(int(ingredient.prot * SCALING_FACTOR))
        carbs.append(int(ingredient.carbs* SCALING_FACTOR))
        fat.append(int(ingredient.fat * SCALING_FACTOR))
        if ingredient.cal < minCal:
            minCal = ingredient.cal
    
    quantities = VarArray(numIngredients,0,int(10000)) #decision variables
    print quantities
    print "CAL:" + str(calories)
    print "PROT:" + str(prot)
    print "CARBS:" + str(carbs)
    print "FAT:"+ str(fat)

    #initialise model and add constraints
    m = Model(
    #when used in this fashion, the sum constraint acts as the scalar constraint
        Sum(quantities,calories) <= upperbounds[0],
        Sum(quantities,calories) >= lowerbounds[0],
        Sum(quantities,prot) <= upperbounds[1],
        Sum(quantities,prot) >= lowerbounds[1],
        Sum(quantities,carbs) <= upperbounds[2],
        Sum(quantities,carbs) >= lowerbounds[2],
        Sum(quantities,fat) <= upperbounds[3],
        Sum(quantities,fat) >= lowerbounds[3]
        )
    
    print m
    solver = m.load('Mistral')
    
    solver.solve()
    solver.printStatistics()
    print quantities

    return str(quantities)
    

    


def test_generation():
    chicken = Ingredient("Chicken",2.19,0.25,0,0.13,None,None,None,None,None,1)
    pasta = Ingredient("Pasta",3.71,0.13,0.75,0,None,None,None,None,None,1)
    oil = Ingredient("Oil",8.84,0,0,1,None,None,None,None,None,1)
    ingredients = [chicken,pasta,oil]
    
    cal = NutrientRequirement(3000,"=",5)
    prot = NutrientRequirement(150,"=",5)
    carbs = NutrientRequirement(300,"=",5)
    fat = NutrientRequirement(133,"=",5)
    requirements = Requirements(cal,prot,carbs,fat)
    
    generate_meal(requirements,ingredients)

   
test_generation()
