from MealClasses import *
from Numberjack import *
from Mistral import Solver
import math

SCALING_FACTOR = 1000;

class GenerationException(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)
    

def compute_nutrient_bounds(requirements,uppervalues,lowervalues):
    for entry in requirements.items(): 
        nutrient_name = entry[0] #the nutrient being considered
        requirement = entry[1] #the requirement for that nutrient
        if isinstance(requirement,DefiniteNutrientRequirement):
            margin_percentage = requirement.error_margin
            margin = requirement.val * (margin_percentage / 100.0) #calc margin of error for nutrient
            uppervalues[nutrient_name] = int(math.floor((requirement.val + margin) *SCALING_FACTOR))
            lowervalues[nutrient_name] = int(math.ceil((requirement.val - margin) *SCALING_FACTOR))

        
def generate_meal(requirements,ingredients):
    upperbounds = {}
    lowerbounds = {}
    compute_nutrient_bounds(requirements,upperbounds,lowerbounds)
    print upperbounds
    #print lowerbounds

    numIngredients = len(ingredients)           #number of nutrients being considered

    #extract nutritional content of ingredients
    #stored as a map indexed by nutrient name
    #each value is the quantity of of that nutrient for each ingredient
    #we can visualise this as a matrix
    #each row is indexed by nutrient_name, each column is an ingredients breakdown
    nutrient_values = {}
    for nutrient in requirements.nutrients():
        values = []
        for ingredient in ingredients:
            values.append(int(UnitConversions.roundToDecimalPlaces(ingredient.get_val(nutrient), 3) * SCALING_FACTOR))
        nutrient_values[nutrient] = values
    #print "NUTRIENT VALS: " + str(nutrient_values)
    
    quantities = VarArray(numIngredients,0,int(10000)) #decision variables
   
    #initialise model and add constraints
    m = Model()

    #add constraints on nutrients
    for nutrient in requirements.nutrients():
        requirement = requirements.get_requirement(nutrient)
        
        if isinstance(requirement,DefiniteNutrientRequirement): #definite nutrient requirements
            m.add(Sum(quantities,nutrient_values.get(nutrient)) >= lowerbounds.get(nutrient))
            m.add(Sum(quantities,nutrient_values.get(nutrient)) <= upperbounds.get(nutrient))
       
        elif isinstance(requirement,RestrictedNutrientRequirement): #restriction nutrient requirements
            threshold = requirement.threshold() * SCALING_FACTOR
            if requirement.restriction == "<":
                m.add(Sum(quantities,nutrient_values.get(nutrient)) < threshold)
            elif requirement.restriction == ">":
                m.add(Sum(quantities,nutrient_values.get(nutrient)) > threshold)
            elif requirement.restriction == "<=":
                m.add(Sum(quantities,nutrient_values.get(nutrient)) <= threshold)
            elif requirement.restriction == ">=":
                m.add(Sum(quantities,nutrient_values.get(nutrient)) >= threshold)
            else:
                raise GenerationException("Invalid restriction on " + str(nutrient))

    #add constraints for restricted ingredients
    qCursor = 0 #resolves the the quantity variable for the current ingredient
    for ingredient in ingredients:
        if isinstance(ingredient,RestrictedIngredient):
            threshold = ingredient.threshold
            if ingredient.restriction == "<":
                m.add(quantities[qCursor] < threshold)
            elif ingredient.restriction == ">":
                m.add(quantities[qCursor] > threshold)
            elif ingredient.restriction == "=":
                m.add(quantities[qCursor] == threshold)
            elif ingredient.restriction == "<=":
                m.add(quantities[qCursor] <= threshold)
            elif ingredient.restriction == ">=":
                m.add(quantities[qCursor] >= threshold)
            else:
                raise GenerationException("Invalid restriction on " + str(ingredient))
        qCursor += 1
    f = open("output",'a')
    f.write(str(m))
    solver = m.load('Mistral')
    
    solver.solve()
    #solver.printStatistics()
    #print quantities

    return str(quantities)


    
def generate(ingredients,requirements):
    output = generate_meal(requirements = requirements, ingredients = ingredients)

    f = open("output",'a')
    f.write('MEAL GENERATOR: ' +str(output) + "\n")
    f.write('INGREDIENTS:\n')
    for ingredient in ingredients:
        f.write(str(ingredient) + "\n")
    f.close()

    if '{' in output:
        return [0]*len(ingredients)
    output = output.strip('[]').replace(" ","").split(',',len(ingredients))

    #convert back to ounces if necessary
    quantities = []
    for ingredient in ingredients:
        if ingredient.unit == "oz" and not ingredient.fixed:
            quantities.append(int(output.pop(0))/ UnitConversions.OZ_TO_G)
        else:
            quantities.append(int(output.pop(0)))
    return quantities

def test_generation():
    chicken = Ingredient("Chicken",{"calories":219,"protein":25,"fat":13},100,"g",False)
    pasta = RestrictedIngredient("Pasta",{"calories":3.71,"protein":0.13,"carbs":0.75,"fat":0.015},1,"g",True,'<',75)
    oil = Ingredient("Oil",{"calories":8.84,"fat":1},1,"g",True)
    ingredients = [chicken,pasta,oil]
    
    requirements = Requirements()
    requirements.add("calories",DefiniteNutrientRequirement(600,5))
    requirements.add("protein",DefiniteNutrientRequirement(30,1))
    requirements.add("carbs",DefiniteNutrientRequirement(50,1))
    requirements.add("fat",RestrictedNutrientRequirement(30,"<"))

    print generate(ingredients,requirements)

#test_generation();

