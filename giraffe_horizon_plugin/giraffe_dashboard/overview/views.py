'''
Defines one or more views of the panel.

A views can be defined through a class (XyzView) or a method (xyz).
'''

#import logging
#LOG = logging.getLogger(__name__)


#from django.contrib import messages
#from django.views import generic
#from horizon import api
#from horizon import forms
#from horizon import tables
from django import shortcuts

#from .tables import HostsTable


def index(request):
    return shortcuts.render(request, 'giraffe_dashboard/overview/index.html')
