__author__ = 'michael'


''' These classes are wrappers for the FatSecret foods.ingredient_search method results to encapsuate a food.
See http://platform.fatsecret.com/api/Default.aspx?screen=rapiref&method=foods.ingredient_search
for service description.
Instance variables corresponds to the data returned by the service.
Note that the 'type' value determines if the food is Generic or Branded, and is not stored with the food.
'''

class GenericFoodDescription(object):
    def __init__(self,name,id,url,description):
        self.name = str(name[0])
        self.id = int(id[0])
        self.url = str(url[0])
        self.description = str(description)

class BrandedFoodDescription(GenericFoodDescription):
    def __init__(self,name,id,url,description,brand):
        super(BrandedFoodDescription,self).__init__(name,id,url,description)
        self.brand = str(brand)


'''
Simple wrapper for capturing food data.
nutrient_values is a dictionary mapping nutrient names to their quantity in standard units (kcal for calories, grams for all else).
See the FatSecretAPI foods.get method for more info.
'''
class Serving(object):
    def __init__(self,serving_description,nutrient_values,quantity,unit,num_units,measurement_description):
        self.description = serving_description
        self.nutrient_vals = nutrient_values
        self.quantity = quantity
        self.unit = unit
        self.num_units = num_units
        self.measurement_description = measurement_description

    def __str__(self):
        output = ""
        output += self.description + "\n"
        for kv in self.nutrient_vals.items():
            output += str(kv[0]) + ": " + str(kv[1]) + "\n"
        return output