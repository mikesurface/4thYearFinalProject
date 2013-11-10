class Requirements:
    def __init__(self,requirements):
        self.requirements = requirements

    def __str__(self):
        output = ""
        for requirement in self.requirements:
            output += (str(requirement.name) + ":\n\t" + str(requirement)) + "\n"
        return output

    def number_of_requirements(self):
        len(requirements)
    
class NutrientRequirement:
    def __init__(self,name,val,restriction,error):
        self.name = name
        self.val = val
        self.restriction = restriction
        self.error_margin = error

    def __str__(self):
        return "Value: " + str(self.val) + " Error Margin: " + str(self.error_margin) + "%"
        
class Ingredient:
    def __init__(self,name,values,restriction,quantity):
        self.name = name
        self.val = values
        self.restriction = restriction


        
def testClasses():
    requirements = []
    
    calories = NutrientRequirement("Calories",2000,"=",5)
    protein = NutrientRequirement("Protein",100,"=",5)
    carb = NutrientRequirement("Carbs",200,"=",5)
    fat = NutrientRequirement("Fat",50,"=",5)

    requirements.append(calories)
    requirements.append(protein)
    requirements.append(carb)
    requirements.append(fat)

    requirementsObject = Requirements(requirements)
    print requirementsObject

testClasses()
