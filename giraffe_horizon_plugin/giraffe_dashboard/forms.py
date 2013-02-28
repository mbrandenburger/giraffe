__author__ = 'omihelic, fbahr'

from datetime import date
from django.utils import dates
from horizon import forms


class DateMeterForm(forms.Form):
    """
    A simple form for selecting a start date.
    """
    month = forms.ChoiceField(choices=dates.MONTHS.items())
    year = forms.ChoiceField()
    day = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:60px'}))
    meter = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        meter_list = []
        if 'meters' in kwargs:
            meters = kwargs.get('meters')
            for m in sum([meters] if meters else [], []):
                meter_list.append((m.id, m.name))
            del kwargs['meters']
        super(DateMeterForm, self).__init__(*args, **kwargs)

        # fill meters
        self.fields['meter'].choices = meter_list

        # fill years
        today = date.today()
        years = [(today.year + i,) * 2 for i in range(2)]
        years.reverse()
        self.fields['year'].choices = years

        # placeholder for days
        self.fields['day'].choices = []
