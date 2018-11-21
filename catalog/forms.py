import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from catalog.models import BookInstance

class RenewBookForm(forms.Form):
    """
    simple form which allows librarians to update the due date of book instances
    """
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks from now (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # check that date is not in the past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # check that the date is in the valid range
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data


class RenewBookModelForm(forms.ModelForm):

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # check that date is not in the past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # check that the date is in the valid range
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks from now (default 3).')}

