class Ingredient(object):
	def __init__(self, nutrients):
		self.nutrients = nutrients
class GoalSet(object):
	def __init__(self,nutrientGoals,bodyGoals):
		self.nutrient_goals = nutrientGoals
		self.body_goals = bodyGoals

	def bodyGoalsPretty(self):
		output = ""
		for goal in self.body_goals.keys():
			output += goal + ": " + str(self.body_goals.get(goal))
		print output
	
ingredient = Ingredient({"calories":400, "protein":20, "carbs":40, "fat":10})
for nutrient in ingredient.nutrients.keys():
	print nutrient + " "+ str(ingredient.nutrients.get(nutrient))
print "_____________________________________________"

goalSet = GoalSet({"calories":2400,"protein":90,"carbs":180,"fat":20}, {"weight":175})
goalSet.bodyGoalsPretty()
