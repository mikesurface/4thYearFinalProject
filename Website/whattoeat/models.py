from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
#defaults
from whattoeat.solver_backend import UnitConversions

DEFAULT_ERROR_MARGIN = 5

#choices

#also defines an ordering describing how these nutrients are conventionally viewed
ALLOWED_NUTRIENTS = (
    ('calories', 'Calories'), ('protein', 'Protein'), ('carbs', 'Total Carbohydrate'),
    ('fat', 'Total Fat'), ('satfat', 'Saturated Fat'), ('salt', 'Salt'), ('sugar', 'Sugar'),
    ('fibre', 'Fibre'),
)
GENDERS = (('m', 'Male'), ('f', 'Female'),)
GOALS = (('maintain weight', 'Maintain Weight'), ('lose weight', 'Lose Weight'), ('gain weight', 'Gain Weight'))
RESTRICTIONS = (('<', 'less than'), ('>', 'more than'), ('>=', 'at least'), ('<=', 'no more than'),)

# Create your models here.



class DietProfile(models.Model):
    """
        User Profile. Contains extra data about the user expressing their vital statistics and requirements.
        The attributes are:
         user: the user to which this profile belongs (foreign key reference)
         gender: m for male, f for female (charfield, max len 1)
         age: the users age (integer)
         height: the users height in metres (float)
         weight: the users weight in kilograms (float)

        All fields are required.
    """
    user = models.ForeignKey(User, unique=True, primary_key=True)
    gender = models.CharField(max_length=1, blank=False, choices=GENDERS, null=True)
    age = models.IntegerField(blank=False, null=True)
    height = models.FloatField(blank=False, null=True)
    weight = models.FloatField(blank=False, null=True)
    goal = models.CharField(max_length=50, choices=GOALS, null=True)

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
        return round(self.height / UnitConversions.INCHES_TO_M, 1)

    def height_in_cm(self):
        return round(self.height * 100, 1)

    def weight_in_lbs(self):
        return round(self.weight / UnitConversions.POUNDS_TO_KILOS, 1)

    def __str__(self):
        return (
            "{user:" + self.user.get_full_name() + ",height:" + str(self.height) + ",weight:" + str(self.weight)
            + ",age:" + str(self.age)
            + ",gender:" + self.gender + ",goal:" + self.goal + "}"
        )

    def add_daily_requirements_set(self, num_meals_per_day):
        """
            Create a new daily requirements set, or update the old one
            Returns the set
        """
        try:
            existing = DailyRequirementsSet.objects.get(profile=self.pk)
            existing.num_meals_per_day = num_meals_per_day
            existing.save()
            return existing
        except ObjectDoesNotExist:
            new = DailyRequirementsSet(profile=self.pk, num_meals_per_day=num_meals_per_day)
            new.save()
            return new

    def get_daily_requirements_set(self):
        """
            Get all the meal requirements sets associated with this profile
            Returns a QuerySet of meal requirements set
            None in no sets are found
        """
        try:
            set = DailyRequirementsSet.objects.get(profile=self.pk)
            return set
        except ObjectDoesNotExist:
            return None


    def get_all_meal_requirements_sets(self):
        try:
            sets = MealRequirementsSet.objects.filter(profile=self.pk)
            return sets
        except ObjectDoesNotExist:
            return None


    def get_meal_requirements_set(self, name):
        """
            Get a meal requirements set by name
            Returns the meal requirements set if it exists
            None if it does not
        """
        try:
            set = MealRequirementsSet.objects.get(profile=self.pk, name=name)
            return set
        except ObjectDoesNotExist:
            return None


    def add_meal_requirements_set(self, name):
        """
            Add a new meal requirements set
            Returns the set if a new set added

        """
        try:
            set = MealRequirementsSet.objects.get(profile=self.pk, name=name)
        except ObjectDoesNotExist:
            set = MealRequirementsSet(profile=self.pk,name=name)
        set.save()
        return set


    def delete_meal_requirements_set(self,name):
        '''
        Removes a meal requirements set, deleting it and any attached requirements
        Returns True if something was deleted
        False if no such meal requirements set was found
        '''
        try:
            set = self.get_meal_requirements_set(name)
            set.clear_requirements()
            set.delete()
            return True
        except ObjectDoesNotExist:
            return False


#Associate profile with corresponding user
User.profile = property(lambda u: DietProfile.objects.get_or_create(user=u)[0])


class RequirementsSet(models.Model):
    """
        Defines a base class for a set of requirements
        The attributes are:
        id: implicit id set up by Django
        user_profile: foreign key reference to a user profile to which this set of requirements belong
    """
    profile = models.PositiveIntegerField() #user may have multiple requirements sets

    class Meta:
        abstract = True


class DailyRequirementsSet(RequirementsSet):
    """
       Defines a daily requirements set
       The attributes are:
        num_meals_per_day: the number of solver_backend the user wishes to eat per day
       The user may have only one of these at any time
   """

    num_meals_per_day = models.PositiveIntegerField()


    def get_requirement_by_name(self, nutrient_name):
        """
            Get a requirement by the nutrient name.
            Returns the requirement if found
            None if not found
        """
        req = None
        try:
            req = DefiniteDietRequirement.objects.get(set_id=self.pk, name=nutrient_name,daily=True)
        except ObjectDoesNotExist:
            pass
        try:
            req = RestrictedDietRequirement.objects.get(set_id=self.pk, name=nutrient_name,daily=True)
        except ObjectDoesNotExist:
            pass
        return req


    def add_definite_requirement(self, nutrient_name, value, error):
        """
            Add a new definite requirement to the set. If a definite requirement exists on this nutrient it is overwritten
            Return True if the requirement is added
            False if a requirement on this nutrient exists already but not as a definite requirement
        """
        #check to see if a requirement on the nutrient already exists
        req = self.get_requirement_by_name(nutrient_name)
        if isinstance(req, DefiniteDietRequirement):
            #overwrite
            req.value = value
            req.error = error
            req.save()
            return True

        elif isinstance(req, RestrictedDietRequirement):
            #exists as restricted
            return False

        else:
        #new
            new = DefiniteDietRequirement(set_id=self.pk, name=nutrient_name, value=value, error=error,daily=True)
            new.save()
            return True


    def get_definite_requirement(self, nutrient_name):
        """
            Get the definite requirement on a given nutrient.
            If found return the requirement.
            Else return None
        """

        try:
            req = DefiniteDietRequirement.objects.get(set_id=self.pk, name=nutrient_name,daily = True)
            return req
        except ObjectDoesNotExist:
            return None


    def get_all_definite_requirements(self):
        """
            Get all the definite requirements.
            Returns a QuerySet of definite requirements, or None if none exist
        """
        try:
            reqs = DefiniteDietRequirement.objects.filter(set_id=self.pk,daily=True)
            return reqs
        except ObjectDoesNotExist:
            return None


    def add_restricted_requirement(self, nutrient_name, value, restriction):
        """
           Add a new restricted requirement to the set. If a restricted requirement exists on this nutrient it is overwritten
          Return True if the requirement is added
          False if a requirement on this nutrient exists already but not as a definite requirement
        """

        #check to see if a requirement on the nutrient already exists
        req = self.get_requirement_by_name(nutrient_name)
        if isinstance(req, RestrictedDietRequirement):
            #overwrite
            req.value = value
            req.restriction = restriction
            req.save()
            return True

        elif isinstance(req, DefiniteDietRequirement):
            #exists as definite
            return False

        else:
        #new
            new = RestrictedDietRequirement(set_id=self.pk, name=nutrient_name, value=value, restriction=restriction, daily=True)
            new.save()
            return True


    def get_restricted_requirement(self, nutrient_name):
        """
            Get the restricted requirement on a given nutrient.
            If found return the requirement.
            Else return None
        """

        try:
            req = RestrictedDietRequirement.objects.get(set_id=self.pk, name=nutrient_name,daily=True)
            return req
        except ObjectDoesNotExist:
            return None


    def get_all_restricted_requirements(self):
        """
            Get all the definite requirements.
            Returns a QuerySet of definite requirements, or None if none exist
        """

        try:
            reqs = RestrictedDietRequirement.objects.filter(set_id=self.pk,daily=True)
            return reqs
        except ObjectDoesNotExist:
            return None


    def clear_requirements(self):
        """
            Delete all requirements on this set
        """
        #clear definite requirements
        try:
            def_reqs = DefiniteDietRequirement.objects.filter(set_id=self.pk, daily=True)
            def_reqs.delete()
        except ObjectDoesNotExist:
            pass

        #delete restricted requirements
        try:
            res_reqs = RestrictedDietRequirement.objects.filter(set_id=self.pk, daily=True)
            res_reqs.delete()
        except ObjectDoesNotExist:
            pass

        return


    def get_conventional_ordering(self):
        """
            Returns all the nutrients in the set in conventional order, as defined by ALLOWED_NUTRIENTS
            Returns an empty list if this set has no requirements
            Returns a 2d list otherwise. For each entry, the first item is the printable nutrient name, the second is
            the value or restriction
        """
        reqs = []
        for nut in ALLOWED_NUTRIENTS:
            r = self.get_requirement_by_name(nut[0])
            if r:
                reqs.append((nut[1], r.printable_constraint()))
        return reqs


class MealRequirementsSet(RequirementsSet):
    """
        Defines a requirements profile for a meal
        The attributes are:
         name: the name of the profile
    """
    name = models.CharField(max_length=100)


    def get_requirement_by_name(self, nutrient_name):
        """
            Get a requirement by the nutrient name.
            Returns the requirement if found
            None if not found
        """
        req = None
        try:
            req = DefiniteDietRequirement.objects.get(set_id=self.pk, name=nutrient_name,daily=False)
        except ObjectDoesNotExist:
            pass
        try:
            req = RestrictedDietRequirement.objects.get(set_id=self.pk, name=nutrient_name,daily=False)
        except ObjectDoesNotExist:
            pass
        return req


    def add_definite_requirement(self, nutrient_name, value, error):
        """
            Add a new definite requirement to the set. If a definite requirement exists on this nutrient it is overwritten
            Return True if the requirement is added
            False if a requirement on this nutrient exists already but not as a definite requirement
        """
        #check to see if a requirement on the nutrient already exists
        req = self.get_requirement_by_name(nutrient_name)
        if isinstance(req, DefiniteDietRequirement):
            #overwrite
            req.value = value
            req.error = error
            req.save()
            return True

        elif isinstance(req, RestrictedDietRequirement):
            #exists as restricted
            return False

        else:
        #new
            new = DefiniteDietRequirement(set_id=self.pk, name=nutrient_name, value=value, error=error,daily=False)
            new.save()
            return True


    def get_definite_requirement(self, nutrient_name):
        """
            Get the definite requirement on a given nutrient.
            If found return the requirement.
            Else return None
        """

        try:
            req = DefiniteDietRequirement.objects.get(set_id=self.pk, name=nutrient_name,daily=False)
            return req
        except ObjectDoesNotExist:
            return None


    def get_all_definite_requirements(self):
        """
            Get all the definite requirements.
            Returns a QuerySet of definite requirements, or None if none exist
        """
        try:
            reqs = DefiniteDietRequirement.objects.filter(set_id=self.pk,daily=False)
            return reqs
        except ObjectDoesNotExist:
            return None

    def add_restricted_requirement(self, nutrient_name, value, restriction):
        """
           Add a new restricted requirement to the set. If a restricted requirement exists on this nutrient it is overwritten
          Return True if the requirement is added
          False if a requirement on this nutrient exists already but not as a definite requirement
        """

        #check to see if a requirement on the nutrient already exists
        req = self.get_requirement_by_name(nutrient_name)
        if isinstance(req, RestrictedDietRequirement):
            #overwrite
            req.value = value
            req.restriction = restriction
            req.save()
            return True

        elif isinstance(req, DefiniteDietRequirement):
            #exists as definite
            return False

        else:
        #new
            new = RestrictedDietRequirement(set_id=self.pk, name=nutrient_name, value=value, restriction=restriction, daily=False)
            new.save()
            return True


    def get_restricted_requirement(self, nutrient_name):
        """
            Get the restricted requirement on a given nutrient.
            If found return the requirement.
            Else return None
        """

        try:
            req = RestrictedDietRequirement.objects.get(set_id=self.pk, name=nutrient_name, daily=False)
            return req
        except ObjectDoesNotExist:
            return None

    def get_all_restricted_requirements(self):
        """
            Get all the definite requirements.
            Returns a QuerySet of definite requirements, or None if none exist
        """

        try:
            reqs = RestrictedDietRequirement.objects.filter(set_id=self.pk, daily=False)
            return reqs
        except ObjectDoesNotExist:
            return None


    def clear_requirements(self):
        """
            Delete all requirements on this set
        """
        #clear definite requirements
        try:
            def_reqs = DefiniteDietRequirement.objects.filter(set_id=self.pk, daily=False)
            def_reqs.delete()
        except ObjectDoesNotExist:
            pass
            #delete restricted requirements
        try:
            res_reqs = RestrictedDietRequirement.objects.filter(set_id=self.pk, daily=False)
            res_reqs.delete()
        except:
            pass

        return


    def get_conventional_ordering(self):
        """
            Returns all the nutrients in the set in conventional order, as defined by ALLOWED_NUTRIENTS
            Returns an empty list if this set has no requirements
            Returns a 2d list otherwise. For each entry, the first item is the printable nutrient name, the second is
            the value or restriction
        """
        reqs = []
        for nut in ALLOWED_NUTRIENTS:
            r = self.get_requirement_by_name(nut[0])
            if r:
                reqs.append((nut[1], r.printable_constraint()))

        return reqs

    def __str__(self):
        return self.name


class DietRequirement(models.Model):
    """
        Base class for a nutritional requirement.
        The attributes are:
         Set_id: the id of the requirements set to which this requirment belong
         daily: boolean flag, denotes if this requirement is a daily requirement
         Name: the name of the nutrient on which the requirement is set (charfield)
         Value: the value required or the threshold acceptable value for the nutrient (float)

         All values are required.
         Note this class is abstract and does not exist in the model. Use a subclass instead.
    """

    #foreign key reference to profile of user to whom the requirement belongs
    #not unique since there can be multiple requirements on one profile
    #should never be accessed directly, use methods in RequirementsSet
    set_id = models.PositiveIntegerField()
    daily = models.BooleanField()
    name = models.CharField(max_length=60, choices=ALLOWED_NUTRIENTS, blank=False)
    value = models.FloatField(blank=False)

    class Meta:
        abstract = True #does not exist as a table in the model

    def __str__(self):
        output = ""
        output += self.name + "\n"
        output += str(self.value)
        return output

    def value_rounded(self):
        return round(self.value, 1)

    def value_mg(self):
        return self.value * 1000

    def printable_value(self):
        if self.name == "calories":
            return str(self.value_rounded()) + "kcal"
        else:
            return str(self.value_rounded()) + "g"


class DefiniteDietRequirement(DietRequirement):
    """
        Defines a definite nutritional requirement
        The attributes are:
         error: the error margin (as a percentage) allowed in calculations

        If a value for error is not supplied, a default will be used.
    """
    error = models.IntegerField(default=DEFAULT_ERROR_MARGIN, blank=True) #default error used if none provided

    def __str__(self):
        output = super(DefiniteDietRequirement, self).__str__() + "\n"
        output += str(self.error)
        return output

    def printable_constraint(self):
        return "Within " + str(self.error) + "% of " + str(self.printable_value())





class RestrictedDietRequirement(DietRequirement):
    """
        Defines a restricted nutritional requirement
        The attributes are:
         restriction: this should be either <,>,<= or >=

        All fields are required.
    """
    restriction = models.CharField(max_length=2, blank=False, choices=RESTRICTIONS) #can be <,>,<= or >=

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
        output = super(RestrictedDietRequirement, self).__str__() + "\n"
        output += self.printable_restriction()
        return output

    def printable_constraint(self):
        return self.printable_restriction() + " " + str(self.printable_value())


