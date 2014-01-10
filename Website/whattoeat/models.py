from django.db import models
from django.contrib.auth.models import User
#defaults
from whattoeat.meals import UnitConversions

DEFAULT_ERROR_MARGIN = 5

#choices
GENDERS = (('m','Male'),('f','Female'),)
GOALS = (('maintain weight','Maintain Weight'),('lose weight','Lose Weight'),('gain weight','Gain Weight'))
RESTRICTIONS = (('<','less than'),('>','more than'),('>=','at least'),('<=','no more than'),)

# Create your models here.
'''
User Profile. Contains extra data about the user expressing their vital statistics and requirements.
The attributes are:
 user: the user to which this profile belongs (foreign key reference)
 gender: m for male, f for female (charfield, max len 1)
 age: the users age (integer)
 height: the users height in metres (float)
 weight: the users weight in kilograms (float)

All fields are required.
'''
class DietProfile(models.Model):
    user = models.ForeignKey(User,unique=True,primary_key=True)
    gender = models.CharField(max_length=1,blank=False,choices=GENDERS,null=True)
    age = models.IntegerField(blank=False,null=True)
    height = models.FloatField(blank=False,null=True)
    weight= models.FloatField(blank=False,null=True)
    goal = models.CharField(max_length=50,choices=GOALS,null=True)

    def gender_printable(self):
        if self.gender == 'm':
            return 'Male'
        else:
            return 'Female'

    def goal_printable(self):
        if self.goal == 'maintain weight':
            return 'Maintain Weight'
        elif self.goal == 'lose weight':
            return 'Lose Weight'
        else:
            return 'Gain Weight'

    def height_in_inches(self):
        return UnitConversions.roundToDecimalPlaces(self.height / UnitConversions.INCHES_TO_M,1)

    def height_in_cm(self):
        return UnitConversions.roundToDecimalPlaces(self.height * 100,1)

    def weight_in_lbs(self):
        return UnitConversions.roundToDecimalPlaces(self.weight / UnitConversions.POUNDS_TO_KILOS,1)


#Associate profile with corresponding user
User.profile = property(lambda u: DietProfile.objects.get_or_create(user=u)[0])



'''
Defines a base class for a set of requirements
The attributes are:
 id: implicit id set up by Django
 user_profile: foreign key reference to a user profile to which this set of requirements belong

'''
class RequirementsSet(models.Model):
    profile = models.ForeignKey(DietProfile,unique=False ) #user may have multiple requirements sets


'''
Defines a daily requirements set
The attributes are:
 num_meals_per_day: the number of meals the user wishes to eat per day
The user may have only one of these at any time
'''
class DailyRequirementsSet(RequirementsSet):
    num_meals_per_day = models.IntegerField()


'''
Defines a requirements profile for a meal
The attributes are:
 name: the name of the profile
'''
class MealRequirementsSet(RequirementsSet):
    name = models.CharField(max_length=100)

'''
Base class for a nutritional requirement.
The attributes are:
 Profile: the profile the requirement is associated with
 Name: the name of the nutrient on which the requirement is set (charfield)
 Value: the value required or the threshold acceptable value for the nutrient (float)

 All values are required.
 Note this class is abstract and does not exist in the model. Use a subclass instead.
'''
class DietRequirement(models.Model):
    #foreign key reference to profile of user to whom the requirement belongs
    #not unique since there can be multiple requirements on one profile
    set = models.ForeignKey(RequirementsSet,unique=False)

    name = models.CharField(max_length=60,blank=False)
    value = models.FloatField(blank=False)

    class Meta:
        abstract = True #does not exist as a table in the model

    def __str__(self):
        output = ""
        output += self.name+"\n"
        output += str(self.value)
        return output

    def value_rounded(self):
        return UnitConversions.roundToDecimalPlaces(self.value,2)

    def value_mg(self):
        return self.value * 1000

'''
Defines a definite nutritional requirement
The attributes are:
 error: the error margin (as a percentage) allowed in calculations

If a value for error is not supplied, a default will be used.
'''
class DefiniteDietRequirement(DietRequirement):
    error = models.IntegerField(default=DEFAULT_ERROR_MARGIN,blank=True) #default error used if none provided

    def __str__(self):
        output = super(DefiniteDietRequirement,self).__str__() + "\n"
        output += str(self.error)
        return output

'''
Defines a restricted nutritional requirement
The attributes are:
 restriction: this should be either <,>,<= or >=

All fields are required.
'''
class RestrictedDietRequirement(DietRequirement):
    restriction = models.CharField(max_length=2,blank=False,choices=RESTRICTIONS) #can be <,>,<= or >=

    def printable_restriction(self):
        if self.restriction == '<':
            return 'less than'
        elif self.restriction == '>':
            return 'more than'
        elif self.restriction == '<=':
            return 'no more than'
        elif self.restriction == '>=':
            return 'at least'
        else:
            return 'UNKNOWN RESTRICTION'

    def __str__(self):
        output = super(RestrictedDietRequirement,self).__str__() + "\n"
        output += self.printable_restriction()
        return output
