#Module containing representations of key components in meal generation
from whattoeat.solver_backend import UnitConversions
from whattoeat.solver_backend.default_values import ALLOWED_INGREDIENT_RESTRICTIONS


class MealClassException(Exception):

    def __init__(self,message):
        self.message = message

    def __str__(self):
        return self.message


class NutrientRequirement(object):
    """Holds the requirements for a specific nutrient as a required value"""
    def __init__(self,val):
          self.val = float(val)

    def __str__(self):
        return str(" Value: " + str(self.val))

class DefiniteNutrientRequirement(NutrientRequirement):
    """Holds a definite requirement. That is a requirement where we wish to achieve
    a specific value or be within an acceptable range of values"""

    def __init__(self,val,error):
        super(DefiniteNutrientRequirement,self).__init__(val)
        error = float(error)

        if error < 0 or error > 100:
            raise MealClassException("Error must be a percentage between 0-100")

        self.error_margin = error

    def __str__(self):
        output = super(DefiniteNutrientRequirement,self).__str__()
        return output + " Error: " + str(self.error_margin)

class RestrictedNutrientRequirement(NutrientRequirement):
    """Holds a restricted requirement. That is a requirement which is specified only in terms of having at least
     or at most a certain value"""

    def __init__(self,threshold,restriction):
        super(RestrictedNutrientRequirement,self).__init__(threshold)
        self.restriction = restriction

    def threshold(self):
        return self.val

    def __str__(self):
        return "Restriction: " + str(self.restriction) + " " + str(self.val)


class Ingredient(object):
    """
    Class for an ingredient and its nutritional content.
    """
    def __init__(self,name,quantity,unit,nutrient_values={},fixed = True):
        self.name = str(name).lower()
        self.quantity = float(quantity)
        self.unit = unit
        self.fixed = fixed
        self.nutrient_values ={}
        for n in nutrient_values.items():
            self.nutrient_values[str(n[0]).lower()] = float(n[1])

    def add_nutrient_val(self,nutrient_name,value):
        nutrient_name = str(nutrient_name).lower()
        self.nutrient_values[nutrient_name] = float(value)


    def remove_nutrient_val(self,nutrient_name):
        nutrient_name = nutrient_name.lower()
        return self.nutrient_values.pop(nutrient_name,0) #default to 0 if no entry for nutrient

    def get_nutrient_val(self,nutrient_name):
        nutrient_name = nutrient_name.lower()
        return self.nutrient_values.get(nutrient_name,0) #default to 0 if no entry for nutrient


    def __str__(self):
       return str(self.quantity)+" "+str(self.unit) + " of " + str(self.name)



class RestrictedIngredient(Ingredient):
    """A restricted ingredient is one where we wish to limit the amount so we use no more than or at least a certain quantity"""
    def __init__(self,name,quantity,unit,threshold,fixed=True,nutrient_values={},restriction="="):
        super(RestrictedIngredient,self).__init__(name,quantity,unit,nutrient_values,fixed)
        self.set_restriction(restriction,threshold)

    def set_restriction(self,restriction,threshold):
        if restriction not in ALLOWED_INGREDIENT_RESTRICTIONS:
            raise MealClassException(str(restriction) + " is not a valid restriction on an ingredient.")
        self.restriction = restriction
        self.threshold = float(threshold)


class Quantity(object):
    def __init__(self,name,quantity,unit):
        self.name = name.lower()
        self.quantity = quantity
        self.unit = unit

