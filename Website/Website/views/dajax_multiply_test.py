from django.shortcuts import render_to_response
from django.template.context import RequestContext

__author__ = 'michael'

def multiply_page(request):
    return render_to_response('dajax_multiply_example.html',context_instance=RequestContext(request))
