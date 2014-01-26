import unittest
from whattoeat.solver_backend.Formulae import *


class FormulaeTest(unittest.TestCase):

    def test_validate_height_and_weight(self):
        #acceptable values
        height = "180.2"
        weight = "89.5"
        self.assertEqual(validate_height(height),180.2)
        self.assertEqual(validate_weight(weight),89.5)

        #unacceptable values
        height = "cheese"
        weight = ""
        with self.assertRaises(FormulaeException):
            validate_height(height)
        with self.assertRaises(FormulaeException):
            validate_weight(weight)

    def test_conversions(self):
        #manual test
        #height in inches
        height = "60"
        #weight in lbs
        weight = "192.5"

        self.assertEqual(convert_height_inches_to_metres(height),1.524)
        self.assertEqual(round(convert_pounds_to_kg(weight),5),87.31646)

    def test_henry_oxford(self):
        #try with invalid details
        gender = "q"
        age = 3
        height = 1.7 #1.7m
        weight = 85 #85kg
        with self.assertRaises(FormulaeException):
            henry_oxford_bmr(height,weight,age,gender)


        #Note input values on height, weight are arbitrary; they dont really have to be representative of the age group
        #to assert the formula is correct

        #age 0-3
        age = 1
        gender = 'm'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),3547.5)
        gender = 'f'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),3492.1)

        #age 3-10
        age = 8
        gender = 'm'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),1715.6)
        gender = 'f'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),2057.5)

        #age 10-18
        age = 14
        gender = 'm'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),2077.2)
        gender = 'f'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),1684.3)

        #age 18-30
        age = 24
        gender = 'm'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),1869.1)
        gender = 'f'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),1647.5)

        #age 30-60
        age = 45
        gender = 'm'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),1751.7)
        gender = 'f'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),1537.1)

        #age 60+
        age = 60
        gender = 'm'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),1632.7)
        gender = 'f'
        self.assertEqual(henry_oxford_bmr(height,weight,age,gender),1450.6)

    def test_PAL(self):
        with self.assertRaises(FormulaeException):
            PAL_lookup(-1)

        #age 0-3
        self.assertEqual(PAL_lookup(0),1.4)
        self.assertEqual(PAL_lookup(2),1.4)

        #age 3-10
        self.assertEqual(PAL_lookup(3),1.58)
        self.assertEqual(PAL_lookup(9),1.58)

        #age 10-18
        self.assertEqual(PAL_lookup(10),1.75)
        self.assertEqual(PAL_lookup(17),1.75)

        #age 18+
        self.assertEqual(PAL_lookup(18),1.63)

    def test_goal(self):
        self.assertEqual(correct_for_goal('lose weight'),-500)
        self.assertEqual(correct_for_goal('gain weight'),200)
        self.assertEqual(correct_for_goal('maintain weight'),0)







if __name__ == '__main__':
    unittest.main()


def run_tests():
    runner = unittest.TextTestRunner()
    runner.run(FormulaeTest)

run_tests()