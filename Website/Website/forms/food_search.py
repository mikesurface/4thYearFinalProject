from django import forms


class FoodSearchForm(forms.Form):
    search_text = forms.CharField(initial='Enter search text')
