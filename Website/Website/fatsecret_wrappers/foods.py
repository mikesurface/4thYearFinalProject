__author__ = 'michael'


''' These classes are wrappers for the FatSecret foods.search method results to encapsuate a food.
See http://platform.fatsecret.com/api/Default.aspx?screen=rapiref&method=foods.search
for service description.
Instance variables corresponds to the data returned by the service.
Note that the 'type' value determines if the food is Generic or Branded, and is not stored with the food.
'''

class GenericFoodDescription(object):
    def __init__(self,name,id,url,description):
        self.name = str(name[0])
        self.id = id
        self.url = str(url[0])
        self.description = str(description)

class BrandedFoodDescription(GenericFoodDescription):
    def __init__(self,name,id,url,description,brand):
        super(BrandedFoodDescription,self).__init__(name,id,url,description)
        self.brand = str(brand)