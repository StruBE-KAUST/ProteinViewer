import logging
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import StrictButton

from django import forms

class SubmitViewerDataForm(forms.Form):
    """Upload files and information to view in the app."""

    sequence = forms.CharField(widget=forms.Textarea())
    pdb_files = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={'multiple': True}
            )
        )
    representation = forms.ChoiceField([
            ('cartoon', 'Cartoon'),
            ('surface', 'Surface')])

    def __init__(self, *args, **kwargs):
        """Create a new form."""
        log = logging.getLogger(__name__)
        log.debug("Enter with args: " + str(args) + " ; " + str(kwargs))

        super(SubmitViewerDataForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('sequence'),
            Field('pdb_files'),
            Field('representation'),
            StrictButton(
                '<span class="ladda-label">View</span>',
                type="submit",
                css_class="btn btn-primary ladda-button submit_button",
                data_style="expand-right",
            )
        )

        log.debug("Exit")
