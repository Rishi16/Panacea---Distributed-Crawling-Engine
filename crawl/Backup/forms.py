from django import forms
from crawl.models import db_batch, db_script

class db_batchForm(forms.ModelForm):
    # team = forms.CharField(max_length=30)
    # batch_name = forms.CharField(max_length=30)
    # input_file = forms.FileField()
    # script_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # proxies_file_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # server_file_name = forms.CharField(max_length=30)
    # region = forms.CharField(max_length=30)
    scheduled_date = forms.DateField(required = True, input_formats=['%d-%m-%Y'])
    def __init__(self, user_id, team, *args, **kwargs):
        super(db_batchForm, self).__init__(*args, **kwargs)
        # self.request = kwargs.pop('request', None)
        # super(MyForm, self).__init__(*args, **kwargs)
        # self.fields['script_name'].queryset = db_script.objects.all().order_by('supplier_name')
        self.fields['script_name'] = forms.ModelChoiceField(queryset=db_script.objects.all().order_by('supplier_name'))

        # self.fields['user_id'].widget.attrs['type'] = "hidden"
        # self.fields['user_id'].widget.attrs.update({'type': 'hidden'})
        self.fields['user_id'].widget.attrs['value'] = user_id

        self.fields['team'].widget.attrs['value'] = team

        self.fields['batch_name'].widget.attrs['class'] = "form-control"
        self.fields['batch_name'].widget.attrs['required'] = ""
        self.fields['batch_name'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please Enter the Batch name')"
        self.fields['batch_name'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['input_file'].widget.attrs['class'] = "form-control"
        self.fields['input_file'].widget.attrs['required'] = ""
        self.fields['input_file'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload input file')"
        self.fields['input_file'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['script_name'].widget.attrs['class'] = "form-control"
        self.fields['script_name'].widget.attrs['required'] = ""
        self.fields['script_name'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please Select script')"
        self.fields['script_name'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['scheduled_date'].widget.attrs['type'] = "text"
        self.fields['scheduled_date'].widget.attrs['required'] = ""
        self.fields['scheduled_date'].widget.attrs['data-field'] = "date"
        self.fields['scheduled_date'].widget.attrs['name'] = "date"

        self.fields['scheduled_time'].widget.attrs['type'] = "text"
        self.fields['scheduled_time'].widget.attrs['required'] = ""
        self.fields['scheduled_time'].widget.attrs['data-field'] = "time"
        self.fields['scheduled_time'].widget.attrs['name'] = "time"



    # def clean(self):
    #     cleaned_data = super(db_batchForm, self).clean()
    #     team = cleaned_data.get('team')
    #     batch_name = cleaned_data.get('batch_name')
    #     input_file = cleaned_data.get('input_file')
    #     script_name = cleaned_data.get('script_name')
    #     if not team and not batch_name and not input_file and not script_name:
    #         raise forms.ValidationError('You have to write something!')
    class Meta:
        model = db_batch
        widgets = {'user_id': forms.HiddenInput(), 'team': forms.HiddenInput()}
        fields = ('user_id', 'team',  'batch_name',  'input_file',  'script_name', 'scheduled_date', 'scheduled_time')

class db_scriptForm(forms.ModelForm):
    # team = forms.CharField(max_length=30)
    # batch_name = forms.CharField(max_length=30)
    # input_file = forms.FileField()
    # script_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # proxies_file_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # server_file_name = forms.CharField(max_length=30)
    # region = forms.CharField(max_length=30)

    def __init__(self, user_id, team, *args, **kwargs):
        super(db_scriptForm, self).__init__(*args, **kwargs)
        # self.request = kwargs.pop('request', None)
        # super(MyForm, self).__init__(*args, **kwargs)

        # self.fields['user_id'].widget.attrs['type'] = "hidden"
        # self.fields['user_id'].widget.attrs.update({'type': 'hidden'})
        self.fields['user_id'].widget.attrs['value'] = user_id

        self.fields['team'].widget.attrs['value'] = team

        self.fields['supplier_name'].widget.attrs['class'] = "form-control"
        self.fields['supplier_name'].widget.attrs['required'] = ""
        self.fields['supplier_name'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please Enter the supplier name')"
        self.fields['supplier_name'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['script_file'].widget.attrs['class'] = "form-control"
        self.fields['script_file'].widget.attrs['required'] = ""
        self.fields['script_file'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['script_file'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['proxy_file'].widget.attrs['class'] = "form-control"
        self.fields['proxy_file'].widget.attrs['required'] = ""
        self.fields['proxy_file'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['proxy_file'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['servers'].widget.attrs['class'] = "form-control"
        self.fields['servers'].widget.attrs['required'] = ""
        self.fields['servers'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['servers'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['timeout'].widget.attrs['class'] = "form-control"
        self.fields['timeout'].widget.attrs['required'] = ""
        self.fields['timeout'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['timeout'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['attempt'].widget.attrs['class'] = "form-control"
        self.fields['attempt'].widget.attrs['required'] = ""
        self.fields['attempt'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['attempt'].widget.attrs['oninput'] = "this.setCustomValidity('')"


    # def clean(self):
    #     cleaned_data = super(db_batchForm, self).clean()
    #     team = cleaned_data.get('team')
    #     batch_name = cleaned_data.get('batch_name')
    #     input_file = cleaned_data.get('input_file')
    #     script_name = cleaned_data.get('script_name')
    #     if not team and not batch_name and not input_file and not script_name:
    #         raise forms.ValidationError('You have to write something!')
    class Meta:
        model = db_script
        widgets = {'user_id': forms.HiddenInput(), 'team': forms.HiddenInput()}
        fields = ('user_id', 'team',  'supplier_name',  'script_file', 'proxy_file', 'servers', 'timeout', 'attempt')
