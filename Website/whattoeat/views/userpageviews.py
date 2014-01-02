from django.http import HttpResponse


def user_page(request, username):
    html = "<html><head><title>%s Homepage</title></head><body>This is the home page for user %s (to be implemented)</body></html>" % (
    username, username)
    return HttpResponse(html)


def saved_meals(request, username):
    html = "<html><head><title>%s's Saved Meals</title></head><body>This pages shows %s's saved meals (to be implemented)</body></html>" % (
    username, username)
    return HttpResponse(html)


def retrieve_saved_meal(request, username, meal_id):
    html = "<html><head><title>Meal %s</title></head><body>This page shows meal %s belonging to %s (to be implemented)</body></html>" % (
    meal_id, meal_id, username)
    return HttpResponse(html)


def personal_info(request, username):
    html = "<html><head><title> %s's Vital Info</title></head><body>This page will let %s see/alter their vital statistics (to be implemented)</body></html>" % (
    username, username)
    return HttpResponse(html)


def mealgenerator(request, username):
    html = "<html><head><title> %s's Meal Generator</title></head><body>This page will let %s use the meal generator (to be implemented)</body></html>" % (
    username, username)
    return HttpResponse(html)
