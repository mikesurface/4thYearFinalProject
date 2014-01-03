from django.db import models
from django.contrib.auth.models import User
#defaults

DEFAULT_ERROR_MARGIN = 5

# Create your models here.


'''
User Profile. Contains extra data about the user expressing their vital statistics and requirements.
The attributes are:
 user: the user to which this profile belongs (foreign key reference)
 age: the users age (integer)
 height: the users height in metres (float)
 weight: the users wieght in kilograms (float)
 num_meals_per_day: the number of meals the user wishes to eat per day

All fields are required.
'''
class DietProfile(models.Model):
    user = models.ForeignKey(User,unique=True)
    age = models.IntegerField(blank=False)
    height = models.FloatField(blank=False)
    weight= models.FloatField(blank=False)

#Associate profile with corresponding user
User.profile = property(lambda u: DietProfile.objects.get_or_create(user=u)[0])

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
    profile = models.ForeignKey(DietProfile,unique=False)

    name = models.CharField(max_length=60,blank=False)
    value = models.FloatField(blank=False)

    class Meta:
        abstract = True #does not exist as a table in the model

'''
Defines a definite nutritional requirement
The attributes are:
 error: the error margin (as a percentage) allowed in calculations

If a value for error is not supplied, a default will be used.
'''
class DefiniteDietRequirement(DietRequirement):
    error = models.IntegerField(default=DEFAULT_ERROR_MARGIN,blank=True) #default error used if none provided

'''
Defines a restricted nutritional requirement
The attributes are:
 restriction: this should be either <,>,<= or >=

All fields are required.
'''
class RestrictedDietRequirement(DietRequirement):
    restriction = models.CharField(max_length=2,blank=False) #can be <,>,<= or >=

'''
Defines a base class for a set of requirements
The attributes are:
 id: implicit id set up by Django
 user_profile: foreign key reference to a user profile to which this set of requirements belong

'''
class RequirementsSet(models.Model):
    profile = models.ForeignKey(DietProfile,unique=False) #user may have multiple requirements sets

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



