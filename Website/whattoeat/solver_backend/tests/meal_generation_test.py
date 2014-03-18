import unittest
from whattoeat.solver_backend.MealClasses import Ingredient, RestrictedIngredient
from whattoeat.solver_backend.MealGeneration import MealGenerator, MealGeneratorException


class MealGenerationTest(unittest.TestCase):

    def setUp(self):
        self.g = MealGenerator()

    def tearDown(self):
        self.g = None

    def test_add_ingredients(self):
        i1 = Ingredient(name="Chicken", quantity=1,unit="g")
        i2 = RestrictedIngredient(name="OIL",quantity=100,unit="ml",threshold="1000")
        self.g.add_ingredient(i1)
        self.g .add_ingredient(i2)

        #test addition
        ingredients = self.g.get_all_ingredients()
        self.assertEqual(2,len(ingredients))
        self.assertEqual("chicken",self.g.get_ingredient("CHICKEN").name)
        self.assertEqual(1000,self.g.get_ingredient("oil").threshold)

        #test removal
        self.g.remove_ingredient("chicken")
        self.assertEqual(self.g.get_ingredient("chicken"),None)
        self.assertEqual(len(self.g.get_all_ingredients()),1)

    def test_add_requirements(self):
        self.g.add_definite_requirement("Calories",1000,"5")
        self.g.add_restricted_requirement("Protein",100,"<")

        #test addition
        self.assertEqual(self.g.get_requirement("calories").val,1000)
        self.assertEqual(self.g.get_requirement("PROTEIN").restriction,"<")

        #test removal
        self.g.remove_requirement("calories")
        self.assertEqual(self.g.get_requirement("CALORIES"),None)

        #exception should be thrown when trying to add a second requirement on a nutrient
        with self.assertRaises(MealGeneratorException):
            self.g.add_restricted_requirement("protein",100,">")
            self.g.add_definite_requirement("protein",100,2)

    def test_solving_all_fixed(self):
        #can only really test that there is a solution when we expect one, since many solutions may be valid
        i1 = Ingredient("Chicken",quantity="100",unit="g")
        i1.add_nutrient_val("Calories","219")
        i1.add_nutrient_val("Protein","25")
        i1.add_nutrient_val("fat",13)

        i2 = Ingredient("Macaroni,whole wheat,cooked",quantity=100,unit="g")
        i2.add_nutrient_val("Calories",124)
        i2.add_nutrient_val("Protein",5)
        i2.add_nutrient_val("carbs","27")
        i2.add_nutrient_val("fat",0.5)

        i3 = Ingredient("Tomato Sauce,canned",quantity="1",unit="cup")
        i3.add_nutrient_val("Calories",70)
        i3.add_nutrient_val("protein",3.2)
        i3.add_nutrient_val("carbs",16)
        i3.add_nutrient_val("fat",0.4)

        self.g.add_ingredient(i1)
        self.g.add_ingredient(i2)
        self.g.add_ingredient(i3)

        #can be satisfied by 8 servings of each ingredient
        self.g.add_definite_requirement("Calories",3304,0)
        self.g.add_restricted_requirement("Protein",250,">")

        #check solver can handle requirements for which only some of the ingredients have info
        self.g.add_restricted_requirement("carbs",3000,"<")

        #test definite requiremet where base val is too high but error range allows a solution
        self.g.add_definite_requirement("fat",122.2,10)

        result = self.g.generate()
        self.assertIsNotNone(result)

        content = result["content"]
        self.assertEqual(content["calories"],3304.0)

        quantities = result["quantities"]
        for s in quantities.values():
            self.assertEqual(s["quantity"],8)




    def test_solving_all_fixed_restricted_ingredients(self):
        i1 = RestrictedIngredient("Tuna 100g","100","g",300,restriction="<=")
        i1.add_nutrient_val("Calories",116)
        i1.add_nutrient_val("Protein",26)
        i1.add_nutrient_val("Fat",1)

        i2 = RestrictedIngredient("Wild rice, cooked","1","cup",2)
        i2.add_nutrient_val("Calories","166")
        i2.add_nutrient_val("Protein",7)
        i2.add_nutrient_val("Carbs","35")
        i2.add_nutrient_val("Fat",0.6)
        i2.add_nutrient_val("SatFat",0.1)
        i2.add_nutrient_val("Fibre",3)
        i2.add_nutrient_val("Sugar",1.2)
        i2.add_nutrient_val("Salt",12.5) #note salt in mg here

        i3 = RestrictedIngredient("Lettuce, iceberg","1","leaf",threshold=10)
        i3.add_nutrient_val("Calories",2)
        i3.add_nutrient_val("carbs",0.4)
        i3.add_nutrient_val("salt",5) #salt in mg

        i4 = RestrictedIngredient("Cheddar Cheese","1","g",10)
        i4.add_nutrient_val("Calories",4.02)
        i4.add_nutrient_val("Protein",0.25)
        i4.add_nutrient_val("carbs",0.013)
        i4.add_nutrient_val("fat",0.33)
        i4.add_nutrient_val("satfat",0.21)

        self.g.add_ingredient(i1)
        self.g.add_ingredient(i2)
        self.g.add_ingredient(i3)
        self.g.add_ingredient(i4)

        self.g.add_definite_requirement("Calories",500,2)
        self.g.add_restricted_requirement("salt",500,"<") #salt in mg here as well
        self.g.add_restricted_requirement("sugar",10,"<")
        self.g.add_restricted_requirement("satfat",10,"<")
        #
        result = self.g.generate()

        #solution is as follows:
        #2 servings of rice
        #1 servings of tuna
        #10 servings of cheese
        #10 servings of lettuce
        #this adds to (with respect to the requirements)
        # 508.2 kcal
        # 2.4g sugar
        # 75mg salt
        # 2.3g saturated fat

        content = result["content"]
        self.assertEqual(content["calories"],508.2)
        self.assertEqual(content["salt"],75)
        self.assertEqual(content["sugar"],2.4)
        self.assertEqual(content["satfat"],2.3)

        quantities = result["quantities"]
        self.assertEqual(quantities[i1.name]["quantity"],1.0)
        self.assertEqual(quantities[i2.name]["quantity"],2.0)
        self.assertEqual(quantities[i3.name]["quantity"],10.0)
        self.assertEqual(quantities[i4.name]["quantity"],10.0)



    def test_solving_non_fixed_ingredients(self):
        i1 = RestrictedIngredient("Tuna 100g","100","g",300,restriction="<=")
        i1.add_nutrient_val("Calories",116)
        i1.add_nutrient_val("Protein",26)
        i1.add_nutrient_val("Fat",1)

        i2 = RestrictedIngredient("Wild rice, cooked","1","cup",2)
        i2.add_nutrient_val("Calories","166")
        i2.add_nutrient_val("Protein",7)
        i2.add_nutrient_val("Carbs","35")
        i2.add_nutrient_val("Fat",0.6)
        i2.add_nutrient_val("SatFat",0.1)
        i2.add_nutrient_val("Fibre",3)
        i2.add_nutrient_val("Sugar",1.2)
        i2.add_nutrient_val("Salt",12.5) #note salt in mg here

        i3 = RestrictedIngredient("Lettuce, iceberg","1","leaf",threshold=10)
        i3.add_nutrient_val("Calories",2)
        i3.add_nutrient_val("carbs",0.4)
        i3.add_nutrient_val("salt",5) #salt in mg

        #add a non-fixed ingredient
        i4 = RestrictedIngredient("Cheddar Cheese","100","g",threshold=10,fixed=False)
        i4.add_nutrient_val("Calories",402)
        i4.add_nutrient_val("Protein",25)
        i4.add_nutrient_val("carbs",1.3)
        i4.add_nutrient_val("fat",33)
        i4.add_nutrient_val("satfat",21)

        self.g.add_ingredient(i1)
        self.g.add_ingredient(i2)
        self.g.add_ingredient(i3)
        self.g.add_ingredient(i4)

        self.g.add_definite_requirement("Calories",500,2)
        self.g.add_restricted_requirement("salt",500,"<") #salt in mg here as well
        self.g.add_restricted_requirement("sugar",10,"<")
        self.g.add_restricted_requirement("satfat",10,"<")

        result = self.g.generate()
        ###
        #should produce the same solution as for
        # 'test_solving_all_fixed_restricted_ingredients' case
        # key is that cheese should be degraded accordingly

        content = result["content"]
        self.assertEqual(content["calories"],508.2)
        self.assertEqual(content["salt"],75)
        self.assertEqual(content["sugar"],2.4)
        self.assertEqual(content["satfat"],2.3)

        quantities = result["quantities"]
        self.assertEqual(quantities[i1.name]["quantity"],1.0)
        self.assertEqual(quantities[i2.name]["quantity"],2.0)
        self.assertEqual(quantities[i3.name]["quantity"],10.0)
        self.assertEqual(quantities[i4.name]["quantity"],10.0)




    def test_non_fixed_with_oz_kg_and_lbs(self):

        #Same test again but with unusual units and degredation
        i1 = RestrictedIngredient("Tuna 100g","100","g",100,restriction="=")
        i1.add_nutrient_val("Calories",116)
        i1.add_nutrient_val("Protein",26)
        i1.add_nutrient_val("Fat",1)

        i2 = RestrictedIngredient("Wild rice, cooked","1","cup",2)
        i2.add_nutrient_val("Calories","166")
        i2.add_nutrient_val("Protein",7)
        i2.add_nutrient_val("Carbs","35")
        i2.add_nutrient_val("Fat",0.6)
        i2.add_nutrient_val("SatFat",0.1)
        i2.add_nutrient_val("Fibre",3)
        i2.add_nutrient_val("Sugar",1.2)
        i2.add_nutrient_val("Salt",12.5) #note salt in mg here

        i3 = RestrictedIngredient("Lettuce, iceberg","1","leaf",threshold=10)
        i3.add_nutrient_val("Calories",2)
        i3.add_nutrient_val("carbs",0.4)
        i3.add_nutrient_val("salt",5) #salt in mg

        i4 = Ingredient("Cheddar Cheese","1","oz",fixed=False)
        i4.add_nutrient_val("Calories",114)
        i4.add_nutrient_val("Protein",7)
        i4.add_nutrient_val("carbs",0.4)
        i4.add_nutrient_val("fat",9)
        i4.add_nutrient_val("satfat",6)

        self.g.add_ingredient(i1)
        self.g.add_ingredient(i2)
        self.g.add_ingredient(i3)
        self.g.add_ingredient(i4)

        self.g.add_definite_requirement("Calories",500,2)
        self.g.add_restricted_requirement("salt",500,"<") #salt in mg here as well
        self.g.add_restricted_requirement("sugar",10,"<")
        self.g.add_restricted_requirement("satfat",10,"<")

        result = self.g.generate()
        print result
        #should produce the same solution as for
        # 'test_solving_all_fixed_restricted_ingredients' case
        # however there is a slight variation due to rounding errors in the oz-g conversion
        # quantities (apart from cheese which is in oz) should remain same as before
        #note that we can deduce the error has come from rounding since only those nutrients to which cheese contributes
        #are different
        # key is that cheese should be degraded accordingly

        content = result["content"]
        self.assertEqual(content["calories"],492.168)
        self.assertEqual(content["salt"],75)
        self.assertEqual(content["sugar"],2.4)
        self.assertEqual(content["satfat"],1.472)

        quantities = result["quantities"]
        self.assertEqual(quantities[i1.name]["quantity"],1.0)
        self.assertEqual(quantities[i2.name]["quantity"],2.0)
        self.assertEqual(quantities[i3.name]["quantity"],10.0)
        self.assertEqual(quantities[i4.name]["quantity"],0.212)


if __name__ == '__main__':
    unittest.main()


def run_tests():
    runner = unittest.TextTestRunner()
    runner.run(MealGenerationTest)

run_tests()