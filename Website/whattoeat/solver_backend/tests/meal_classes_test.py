import unittest
from whattoeat.solver_backend.MealClasses import *


class MealClassTest(unittest.TestCase):

    def test_definite_requirement(self):
        requirement = DefiniteNutrientRequirement(2000,5)
        self.assertEqual(requirement.val,2000)
        self.assertEqual(requirement.error_margin,5)

        requirement = DefiniteNutrientRequirement('2000','5')
        self.assertEqual(requirement.val,2000)
        self.assertEqual(requirement.error_margin,5)

    def test_restricted_requirement(self):
        requirement = RestrictedNutrientRequirement(100,"<")
        self.assertEqual(requirement.val,100)
        self.assertEqual(requirement.restriction,"<")


    def test_requirements(self):
        requirement = DefiniteNutrientRequirement("2000","5")
        requirement2 = RestrictedNutrientRequirement("100","<")
        self.assertEqual(2000,requirement.val)
        self.assertEqual(5,requirement.error_margin)
        self.assertEqual(100,requirement2.val)
        self.assertEqual("<",requirement2.restriction)

        #test error range exception
        with self.assertRaises(MealClassException):
            requirement = DefiniteNutrientRequirement("2000","101")
            requirement = DefiniteNutrientRequirement("2000","-1")

    def test_ingredients(self):
        #test building and name resolution
        nutrient_vals1 = {"CALORIES":1.34,"Protein":2.64,"carbs":0.989}
        ingredient1 =  Ingredient(name="Chicken",nutrient_values=nutrient_vals1,quantity=1,unit="g",fixed=False)
        nutrient_vals2 = {"Calories":"1.34","Protein":"3.9","fat":"2"}
        ingredient2 = Ingredient(name="Oil",nutrient_values=nutrient_vals2,quantity="2",unit="ml",fixed=True)
        self.assertEqual(3.9, ingredient2.get_nutrient_val("PROTEIN"))
        self.assertEquals(1,ingredient1.quantity)
        self.assertEquals(ingredient1.get_nutrient_val("calories"),ingredient2.get_nutrient_val("calories"))
        self.assertEquals(ingredient2.get_nutrient_val("carbs"),0)

        #test add/removal of ingredients
        self.assertEqual(ingredient1.remove_nutrient_val("calories"),1.34)
        self.assertEqual(ingredient1.get_nutrient_val("calories"),0)
        ingredient1.add_nutrient_val("calories","1.34")
        self.assertEqual(ingredient1.remove_nutrient_val("calories"),1.34)

        #test exceptions on add
        with self.assertRaises(ValueError):
            ingredient1.add_nutrient_val(1,1)
            ingredient1.add_nutrient_val("Fat","Cheese")

        #test overwrite behavior of add
        ingredient1.add_nutrient_val("calories",1)
        self.assertEqual(ingredient1.get_nutrient_val("calories"),1)

    def test_restricted_ingredients(self):
        nutrient_vals1 = {"CALORIES":1.34,"Protein":2.64,"carbs":0.989}
        nutrient_vals2 = {"Calories":"1.34","Protein":"3.9","fat":"2"}
        ing1 = RestrictedIngredient("Chicken","100","g","1000",fixed=True,nutrient_values=nutrient_vals2)

        self.assertEqual("=",ing1.restriction)
        self.assertEqual(1000,ing1.threshold)


if __name__ == '__main__':
    unittest.main()


def run_tests():
    runner = unittest.TextTestRunner()
    runner.run(MealClassTest)

run_tests()