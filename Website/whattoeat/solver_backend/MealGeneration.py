from copy import deepcopy
from Mistral2 import Solver
from MealClasses import *
from Numberjack import *
import math
from whattoeat.solver_backend.default_values import SCALING_FACTOR, ALLOWED_REQUIREMENTS_RESTRICTIONS


class GenerationException(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)

class MealGeneratorException(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)

    
def number_places_decimal_accuracy():
    return len(str(SCALING_FACTOR)) -1



class MealGenerator(object):
    def __init__(self):
        self.ingredients = {} #holds the input ingredients in their original quantities
        self.requirements = {} #holds the requirements
        self.ingredients_copy = {}#holds a copy of the ingredients, which may be altered or unit converted as desirec
                                  #overwritten by successive generation calls

    #
    # BUILDER METHODS
    #


    def add_ingredient(self,ingredient):
        if not isinstance(ingredient,Ingredient):
            raise MealGeneratorException("Can only add objects of type Ingredient")
        self.ingredients[ingredient.name] = ingredient


    def add_definite_requirement(self,nutrient_name,target,error_margin):
        nutrient_name = nutrient_name.lower()
        if nutrient_name in self.requirements:
            raise MealGeneratorException("A requirement already exists on nutrient: " + nutrient_name)
        self.requirements[nutrient_name] = DefiniteNutrientRequirement(val=target,error=error_margin)

    def add_restricted_requirement(self,nutrient_name,threshold,restriction):
        nutrient_name = nutrient_name.lower()
        if nutrient_name in self.requirements:
            raise MealGeneratorException("A requirement already exists on nutrient: " + nutrient_name)
        if restriction not in ALLOWED_REQUIREMENTS_RESTRICTIONS:
            raise MealGeneratorException(restriction + " is not a valid restriction for a nutritional requirement")
        self.requirements[nutrient_name] = RestrictedNutrientRequirement(threshold=threshold,restriction=restriction)

    def remove_requirement(self,nutrient_name):
        nutrient_name = nutrient_name.lower()
        return self.requirements.pop(nutrient_name,None)

    def get_requirement(self,nutrient_name):
        nutrient_name = nutrient_name.lower()
        return self.requirements.get(nutrient_name,None)


    def get_all_requirements(self):
        return self.requirements

    def remove_ingredient(self,name):
        return self.ingredients.pop(name.lower(),None)

    def get_ingredient(self,name):
        return self.ingredients.get(name.lower(),None)

    def get_all_ingredients(self):
        return self.ingredients.values()


    def clear_requirements(self):
        requirement = {}

    def clear_ingredients(self):
        ingredients = {}

    def clear(self):
        self.clear_requirements()
        self.clear_ingredients()
    #
    # GENERATION METHODS
    #

    def __compute_nutrient_bounds(self,uppervalues,lowervalues):
        for entry in self.requirements.items():
            nutrient_name = entry[0] #the nutrient being considered
            requirement = entry[1] #the requirement for that nutrient
            if isinstance(requirement,DefiniteNutrientRequirement):
                margin_percentage = requirement.error_margin
                margin = requirement.val * (margin_percentage / 100.0) #calc margin of error for nutrient
                uppervalues[nutrient_name] = int(math.floor((requirement.val + margin) *SCALING_FACTOR))
                lowervalues[nutrient_name] = int(math.ceil((requirement.val - margin) *SCALING_FACTOR))

    def __convert_to_solver_int(self,val):
        #Converts a floating point to an int quantity, rounded and scaled to be used by the solver
        #this works by rounding the float to a defined number of places, then shifting the decimal
        #point by that many places
        try:
            return int(round(val,number_places_decimal_accuracy()) * SCALING_FACTOR)
        except TypeError:
            raise MealGeneratorException("Cannot convert " + str(val) + " to a solver variable")

    def __generate_meal(self,ingredients,printStats=False):
        #decision variables
        #Each variable x_j is the quantity of ingredient I_j in the meal
        quantities = VarArray(len(self.ingredients),1,1000)

        #compute the upper and lower values for definite requirements from error margins
        upperbounds = {}
        lowerbounds = {}
        self.__compute_nutrient_bounds(upperbounds,lowerbounds)

        #extract nutritional content of ingredients
        #stored as a map indexed by nutrient name
        #each vector is the quantity of that nutrient for each ingredient
        #we can visualise this as a matrix
        #each row is indexed by nutrient_name, each column is an ingredients breakdown
        nutrient_values = {}
        for nutrient in self.requirements:
            values = [] #vector of values for the nutrient in each ingredient
            for ingredient in ingredients:
                values.append(self.__convert_to_solver_int(ingredient.get_nutrient_val(nutrient)))

            nutrient_values[nutrient] = values

        #initialise model and add constraints
        m = Model()

        #add constraints on nutrients
        for r in self.requirements.items():
            nutrient = r[0]
            requirement = r[1]

            if isinstance(requirement,DefiniteNutrientRequirement): #definite nutrient requirements
                m.add(Sum(quantities,nutrient_values.get(nutrient)) >= lowerbounds.get(nutrient))
                m.add(Sum(quantities,nutrient_values.get(nutrient)) <= upperbounds.get(nutrient))

            elif isinstance(requirement,RestrictedNutrientRequirement): #restriction nutrient requirements
                threshold = self.__convert_to_solver_int(requirement.threshold())
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
                #must convert the threshold to be an number of servings
                #if for example we give 100g of chicken and want no mpre than 1000g,
                #we are actually saying no more than 10 servings of chicken
                #note if the serving is size 1, the threshold remains unchanges
                threshold = int(ingredient.threshold)

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

        if printStats:
            print "MODEL:"
            print m
            print "VARIABLES:"
            print m.variables


        #build a solver and solve
        solver = Solver(m,quantities)
        solver.setVerbosity(0) #turn off solver stats
        solver.solve()

        if printStats:
            print "QUANTITIES:"
            print quantities


        output = str(quantities)

        #curly brace indicate no solution (the solver prints out the partial assignment it made before failure)
        if '{' in output:
            return None

        #convert the solution into an array
        output = output.strip('[]').replace(" ","").split(',',len(self.ingredients))

        meal = {}
        for i in range(0,len(ingredients)):
            meal[ingredients[i].name] = output[i]

        return meal





    def generate(self,printStats=False):
        #do necessary conversions on ingredients
        #take a copy first
        self.ingredients_copy = deepcopy(self.ingredients)
        ingredients = self.ingredients_copy.values()
        for ingredient in ingredients:
            if not ingredient.fixed:
                #convert quantity of each nutrient to what it would be if quantity was 1
                for item in ingredient.nutrient_values.items():
                    #convert value to that for 1 unit
                    val = item[1] / ingredient.quantity
                    ingredient.remove_nutrient_val(item[0])
                    ingredient.add_nutrient_val(item[0],val)

                    #special conversions for units
                    if ingredient.unit.lower() == "oz":
                        #do second version to degrade values into 1g equivalent
                        val = round(val / UnitConversions.OZ_TO_G,number_places_decimal_accuracy())
                        ingredient.remove_nutrient_val(item[0])
                        ingredient.add_nutrient_val(item[0],val)

                #adjust threshold accordingly if required
                if isinstance(ingredient,RestrictedIngredient):
                    if ingredient.unit.lower() == "oz":
                        ingredient.threshold = ingredient.threshold * UnitConversions.OZ_TO_G

                #finally, now that the nutrients/threshold have been degraded set the quantity to 1
                ingredient.quantity = 1

        if printStats:
            print "____________________________"
            print "INGREDIENTS POST CONVERSION:"
            for i in ingredients:
                print str(i.name) + ": " + str(i.nutrient_values)

        result = self.__generate_meal(ingredients,printStats)


        if printStats:
            print "INGREDIENTS:"
            for ingredient in ingredients:
                print str(ingredient) +": "  + str(ingredient.nutrient_values)


        output = self.__generate_meal(ingredients,printStats)
        if not output:
            return None #no solution

        #convert back to ounces if necessary
        quantities = {}

        for ingredient in ingredients:
            ing_quan = output[ingredient.name]
            if ingredient.unit.lower() == "oz" and not ingredient.fixed:
                quantities[ingredient.name]= round(float(ing_quan)/ UnitConversions.OZ_TO_G,number_places_decimal_accuracy())
            elif ingredient.unit.lower() == "kg" and not ingredient.fixed:
                quantities[ingredient.name] = round(float(ing_quan)/ UnitConversions.KG_TO_G,number_places_decimal_accuracy())
            elif ingredient.unit.lower() == "lbs" and not ingredient.fixed:
                quantities[ingredient.name]= round(float(ing_quan)/UnitConversions.LBS_TO_G,number_places_decimal_accuracy())
            else:
                quantities[ingredient.name]= float(ing_quan)

        if printStats:
            print "______________________________"

        #build a JSON response
        json_out = {}

        #build quantities
        quant = {}
        for q in quantities:
            #if the ingredient was degraded, its quantity is the number of 1g servings to be added
            if not self.ingredients.get(q).fixed:
                serving = 1.0
            else:
                serving = self.ingredients.get(q).quantity

            quant[q] = {"serving":serving,
                        "unit": self.ingredients[q].unit,
                        "quantity":quantities[q],
                        }

        json_out["quantities"] = quant

        #build nutritional content
        content = {}
        for n in self.requirements:
            total = 0.0
            #note we are working with the edited copy of the ingredients
            for ingredient in ingredients:
                #if the ingredient is non-fixed several cases must be considered
                #if the original unit was g,ml etc we can look at the copy for the correct content per serving
                #if the unit was changed (as it would be for oz,lbs or kg, the copy holds the nutritional content for 1g,
                #we need to convert the values in the copy back to that for 1 <unit>, where <unit> is the original unit
                #we can do this easily by taking the values from the original, divided by the original quantity
                #so if we had 2oz, we need the nutritional info for 1oz
                if not ingredient.fixed:
                    if ingredient.unit in ("oz","kg","lbs"):
                        #nutrient was converted and degraded
                        original = self.ingredients[ingredient.name]
                        val = original.get_nutrient_val(n) / original.quantity
                        #now times by the quantity in the meal
                        val = quantities[ingredient.name] * val
                    else:
                        #degradation only, not conversion
                        val = ingredient.get_nutrient_val(n) * quantities[ingredient.name]
                else: #same operation for non-fixed
                    val = ingredient.get_nutrient_val(n) * quantities[ingredient.name]
                total += val

            #round off total and add it
            total = round(total,number_places_decimal_accuracy())
            content[n] = total


        json_out["content"] = content

        return json_out





