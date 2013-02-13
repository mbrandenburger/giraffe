from datetime import date

from django.utils import dates

from horizon import forms


class DateMeterForm(forms.Form):
    """ A simple form for selecting a start date. """
    month = forms.ChoiceField(choices=dates.MONTHS.items())
    year = forms.ChoiceField()
    meter = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        meter_list = []
        if 'meters' in kwargs:
            if kwargs['meters']:
                for m in kwargs['meters']:
                    meter_list.append((m.id, m.name))
            del(kwargs['meters'])
        super(DateMeterForm, self).__init__(*args, **kwargs)

        # fill meters
        self.fields['meter'].choices = meter_list

        # fill years
        today = date.today()
        years = [(year, year) for year in xrange(today.year - 1,
                                                 today.year + 1)]
        years.reverse()
        self.fields['year'].choices = years
