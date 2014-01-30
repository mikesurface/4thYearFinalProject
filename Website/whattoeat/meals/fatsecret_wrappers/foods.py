from whattoeat.meals.ingredient_search.forms import ServingForm

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



class Serving(object):
    '''
    Simple wrapper for capturing food data.
    nutrient_values is a dictionary mapping nutrient names to their quantity in standard units (kcal for calories, grams for all else).
    See the FatSecretAPI foods.get method for more info.
    '''
    def __init__(self,food_name,food_id,serving_id,nutrient_values,quantity,units,metric_quantity=None,metric_units=None):
        self.food_name = food_name
        self.food_id = food_id
        self.serving_id = serving_id
        self.nutrient_vals = nutrient_values #nutrient values dictionary

        self.quantity =quantity#the quantity in terms of a decimal multiple of the units
        self.units = units #the unit the measurement is expressed in

        #optional metric descriptions (where available)
        #should be in g, oz or ml
        self.metric_quantity = metric_quantity
        self.metric_units = metric_units

        #build a description
        self.description = str(quantity) + " " + str(units)
        if self.metric_quantity and self.metric_units:
            self.description += " (" + str(metric_quantity) + " " + str(metric_units) + ")"

       #form for displaying hidden data when required
        initial = {
            'food_name':food_name,
            'food_id':food_id,
            'serving_id':serving_id,
            'description':self.description,
            'quantity':quantity,
            'units':units,
            'calories':nutrient_values['calories'],
            'protein':nutrient_values['protein'],
            'carbs':nutrient_values['carbs'],
            'fat':nutrient_values['fat'],
        }
        #now consider optional data
        if 'satfat' in nutrient_values: initial['satfat'] = nutrient_values['satfat']
        if 'sugar' in nutrient_values: initial['sugar'] = nutrient_values['sugar']
        if 'salt' in nutrient_values: initial['salt'] = nutrient_values['salt']
        if 'fibre' in nutrient_values: initial['fibre'] = nutrient_values['fibre']

        if self.metric_quantity: initial['metric_quantity'] = self.metric_quantity
        if self.metric_units: initial['metric_units'] = self.metric_units

        self.form = ServingForm(initial=initial)



    def __str__(self):
        output = ""
        output += self.description + "\n"
        for kv in self.nutrient_vals.items():
            output += str(kv[0]) + ": " + str(kv[1]) + "\n"
        return output