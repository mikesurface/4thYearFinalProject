from MealClasses import *
from Numberjack import *

def compute_nutrient_bounds(requirements,uppervalues,lowervalues):
    for requirement in requirements.requirements:
        margin_percentage = requirement.error_margin
        margin = requirement.val * (margin_percentage / 100.0)
        uppervalues.append(requirement.val + margin)
        lowervalues.append(requirement.val - margin)

        
def generate_meal(requirements,ingredients):
    upperbounds = []
    lowerbounds = []
    compute_nutrient_bounds(requirements,upperbounds,lowerbounds)

def extract_requirement_levels 
    

def testUpperLower():
    nutrientRequirements = []
    nutrientRequirements.append(NutrientRequirement("Calories",3000,"=",5))
    nutrientRequirements.append(NutrientRequirement("Carbs",1000,"=",10))
    requirements = Requirements(nutrientRequirements)
                                
    uppervalues = []
    lowervalues = []
    compute_nutrient_bounds(requirements,uppervalues,lowervalues)

    print uppervalues
    print lowervalues


    
