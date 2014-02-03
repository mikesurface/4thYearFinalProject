from copy import deepcopy
from Mistral2 import Solver
from MealClasses import *
from Numberjack import *
import math
from whattoeat.solver_backend.default_values import SCALING_FACTOR, ALLOWED_REQUIREMENTS_RESTRICTIONS

class MealGeneratorException(Exception):
    '''Exception class for MealGenerator'''
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)

class TooFewIngredientsException(Exception):
    '''special exception class alerting that more ingredients are required'''
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)
    
def number_places_decimal_accuracy():
    '''The number of decimal places to which the solver is accurate'''
    return len(str(SCALING_FACTOR)) -1



class MealGenerator(object):
    '''
    Defines a solver for the Single Meal Generation Problem.
     Given Ingredients, and nutritional requirements, it may attempt to generate a meal which satisfies the requirements
     from the specified ingredients.

     Some important concepts underly its use
     Ingredients may be specified in any unit and any quantity, such as 100g, 1 cup , 2oz etc. There are however some
     special units which are handled differently in the case of non-fixed ingredients (see below)
     Additionally, ingredients may be fixed or non-fixed. The following is a brief explanation of how these work:
      If an ingredient is fixed, the solver will only attempt to use positive integer multiples of the ingredient.
      If it is non-fixed, it will consider the smallest feasible quantity of the ingredient when solving.
      For example, suppose we give as one of our ingredients 100g of cheese.
      If we make this fixed, the solver can only use multiples of 100g. This should be used when we wish to use a
      standard serving. In this case, 200 g would be a possible quantity but 150 would not.
      If we make this non-fixed (degradable), the solver will work with 1g of the ingredient by taking a copy and
      converting the nutritional content and quantity to the equivalent for 1g. The means that any number of grams is
      now a possible solution, giving a greater degree of flexibility when forming a solution.
      Note that if we had specified 100ml of an ingredient and made it degradable, the solver would use 1ml (and not 1g)
      A special case occurs when the unit is 'oz' (ounces), 'lbs' (pounds) or 'kg' (kilograms). In this case, the solver
      will convert the ingredient to 1g and solve as above, but the quantity in the returned meal will be expressed in
      terms of the original unit.
      Also, cups and similar units must be specified as follows if the ingredient is degradable:
        1 + 1/2 a cup (i.e. 1.5 cups) should be specified as 3 half cups. That is the unit is 'half cup' and the quantity is
        3. Such an ingredient will be degraded to 1 half cup for solving: not to quarter cups or any smaller unit.
        Specifying this as 1.5 cups will make 1.5 the smalled feasible unit, and no real degradation will occur.
      The above must be taken into account when specifying the ingredients to the solver.
      Note that copies of the ingredients are taken when solving: the original ingredients as specified remain intact
      and can be recovered/changed between meal generations

      There are two forms of nutritional requirement which may be specified: Definite and Restricted:
      A definite requirement is of the form 'give me within <error_margin> of <value> for the nutrient <nutrient_name>'
       The error margin must be a percentage (between 0 and 100 inclusive). It is recommended that some small error
       margin be allowed.
       An example is 'calories within 5% of 2000kcal'
      A restricted requirement is the form 'give me <restriction> than <threshold> for the nutrient <nutrient_name>'
       Possible restrictions are ('<','>','<=','>=').
       An example is 'salt < 6g'

     Note that the names given to the nutrients specified in the requirements must match (case insensitive) the names
     given to the nutrients in the ingredients. The solver will only consider the nutrients given in the requirements;
     any extra nutrients given by ingredients will be ignored. Note that if an ingredient does not provide a nutritional
     content for a required nutrient, it will be considered that its value for that nutrient is zero. Therefore, if it
     is zero, there is no need to include it in the ingredients nutritional content.

    '''
    def __init__(self):
        self.ingredients = {} #holds the input ingredients in their original quantities
        self.requirements = {} #holds the requirements
        self.ingredients_copy = {}#holds a copy of the ingredients, which may be altered or unit converted as desirec
                                  #overwritten by successive generation calls

    #
    # Ingredients Methods
    #
    def add_ingredient(self,ingredient):
        '''
        Add a new ingredient to the solver.
        ingredient must be a subclass of Ingredient, or a MealGeneratorException is thrown.
        '''
        if not isinstance(ingredient,Ingredient):
            raise MealGeneratorException("Can only add objects of type Ingredient")
        self.ingredients[ingredient.name] = ingredient

    def remove_ingredient(self,name):
        '''
        Remove an ingredient with the given name.
        Return the ingredient if it exists.
        Return None if no ingredient with that name is found.
        '''
        return self.ingredients.pop(name.lower(),None)

    def get_ingredient(self,name):
        '''
        Get an ingredient with the given name.
        Return the ingredient if it exists.
        Return None if no ingredient with that name is found.
        '''
        return self.ingredients.get(name.lower(),None)


    def get_all_ingredients(self):
        '''return all ingredients in a list'''
        return self.ingredients.values()

    def clear_ingredients(self):
        '''Clears the ingredients in the generator'''
        ingredients = {}

    #
    #Requirements Methods
    #

    def add_definite_requirement(self,nutrient_name,target,error_margin):
        '''Add a definite requirement on a nutrient
        Raises a MealGeneratorException if a requirement on this nutrient already exists
        '''
        nutrient_name = nutrient_name.lower()
        if nutrient_name in self.requirements:
            raise MealGeneratorException("A requirement already exists on nutrient: " + nutrient_name)
        self.requirements[nutrient_name] = DefiniteNutrientRequirement(val=target,error=error_margin)

    def add_restricted_requirement(self,nutrient_name,threshold,restriction):
        '''Add a restricted requirement on a nutrient
        Raises a MealGeneratorException if a requirement on this nutrient already exists
        '''
        nutrient_name = nutrient_name.lower()
        if nutrient_name in self.requirements:
            raise MealGeneratorException("A requirement already exists on nutrient: " + nutrient_name)
        if restriction not in ALLOWED_REQUIREMENTS_RESTRICTIONS:
            raise MealGeneratorException(restriction + " is not a valid restriction for a nutritional requirement")
        self.requirements[nutrient_name] = RestrictedNutrientRequirement(threshold=threshold,restriction=restriction)

    def remove_requirement(self,nutrient_name):
        '''Remove the requirement on a nutrient
        Returns the requirement if it exists
        Returns None if it does not
        '''
        nutrient_name = nutrient_name.lower()
        return self.requirements.pop(nutrient_name,None)

    def get_requirement(self,nutrient_name):
        '''Gets the requirement on a nutrient
        Returns the requirement if it exists
        Returns None otherwise
        '''
        nutrient_name = nutrient_name.lower()
        return self.requirements.get(nutrient_name,None)


    def get_all_requirements(self):
        '''Returns a dictionary of requirements, keyed by nutrient name'''
        return self.requirements


    def clear_requirements(self):
        '''Clears the requirements on the generator'''
        requirement = {}



    def clear(self):
        '''Clears all ingredients and requirements in the generator'''
        self.clear_requirements()
        self.clear_ingredients()

    #
    # GENERATION METHODS
    #

    def __compute_nutrient_bounds(self,uppervalues,lowervalues):
        #Works out the upper and lower bounds for definite requirements from the error margin
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
        quantities = VarArray(len(self.ingredients),0,1000)

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


            try:
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
                        raise MealGeneratorException("Invalid restriction on " + str(nutrient))

            except NotImplementedError: #only thrown by very rare numberjack errors
                continue

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
                    raise MealGeneratorException("Invalid restriction on " + str(ingredient))
            qCursor += 1

        if printStats:
            print "MODEL:"
            print m
            print "VARIABLES:"
            print m.variables


        #build a solver and solve
        try:
            solver = Solver(m,quantities)
        except NotImplementedError:
            raise TooFewIngredientsException("Empty expressions occured due to a lack of ingredients") #occurs ocassionaly when only one ingredient is user

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
        '''
        Generate a meal from the current ingredrients and requirments.
        If a solution is found, a JSON response is returned with the following structure:
        {'quantities':{
            <food_name0>:{'serving':<serving0>,'unit;:<unit0>,'quantity':<quantity0>},
            <food_name1>:{'serving':<serving1>,'unit;:<unit1>,'quantity':<quantity1>},
            ....
            }
         'content':{
            <nutrient0>:<total0>,
            <nutrient1>:<total1>,
            ....
        }

        'quantities' holds the amount of each ingredient in the constructed meal
        For each entry, the serving is the serving size
                        the unit is the unit of the serving size (eg g,oz,etc)
                        the quantity is the number of servings in the meal
        'content' holds the nutritional content of the meal
        Each pair is a nutrient name and the total quantity of that nutrient in the meal.

        If no solution can be found, None is returned.

        The solver must contain at least one requirement and one ingredient before this is called.
        This method may raise a MealGenerator exception under a number of circumstances.
        If the printStats flag is set to True, the generator will print debug info including the underlying solver model
        and variables.
        '''
        if len(self.ingredients) < 1 or len(self.requirements) < 1:
            raise MealGeneratorException("Need at least one ingredient and one requirement")

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

            else:
                #if the ingredient is fixed, we need to consider the threshold as a multiple
                #of the given serving
                if isinstance(ingredient,RestrictedIngredient):
                    ingredient.threshold = ingredient.threshold / ingredient.quantity

        if printStats:
            print "____________________________"
            print "REQUIREMENTS: "
            for req in self.requirements:
                print str(req) + " " + str(self.requirements[req])
            print
            print "INGREDIENTS POST CONVERSION:"
            for i in ingredients:
                print str(i.name) + ": "
                for n in i.nutrient_values:
                    print " " + str(n) + ": " + str(i.get_nutrient_val(n))
            print

        #Attempt to generate the meal
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





