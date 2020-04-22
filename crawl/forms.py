from django import forms
from django.forms import ValidationError
from crawl.models import db_batch, db_script
import re

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

        self.fields['input_field_mapping'].widget.attrs['class'] = "form-control"
        self.fields['input_field_mapping'].widget.attrs['required'] = ""
        self.fields['input_field_mapping'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['input_field_mapping'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['output_field_mapping'].widget.attrs['class'] = "form-control"
        self.fields['output_field_mapping'].widget.attrs['required'] = ""
        self.fields['output_field_mapping'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['output_field_mapping'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['timeout'].widget.attrs['class'] = "form-control"
        self.fields['timeout'].widget.attrs['required'] = ""
        self.fields['timeout'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['timeout'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['attempt'].widget.attrs['class'] = "form-control"
        self.fields['attempt'].widget.attrs['required'] = ""
        self.fields['attempt'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['attempt'].widget.attrs['oninput'] = "this.setCustomValidity('')"

    def clean(self):
        print('validating script')
        super(db_scriptForm, self).clean()
        input_field_mapping = self.cleaned_data.get('input_field_mapping')
        output_field_mapping = self.cleaned_data.get('output_field_mapping')
        servers = self.cleaned_data.get('servers')
        try:
            if not type(eval(input_field_mapping)) == type([]):
                self._errors['Input Field mapping:'] = self.error_class([
                    'Incorrect list format. Please follow: ["your_column1","your_column2"]'])
        except:
            self._errors['Input Field mapping:'] = self.error_class([
                'Incorrect list format. Please follow: ["your_column1","your_column2"]'])
            # self.add_error('input_field_mapping', 'Incorrect list format. Please follow: ["your_column1","your_column2"]')
            # raise ValidationError('Incorrect list format. Please follow: ["your_column1","your_column2"]')
        try:
            if not type(eval(output_field_mapping)) == type([]):
                self._errors['Output Field mapping:'] = self.error_class([
                    'Incorrect list format. Please follow: ["your_column1","your_column2"]'])
        except:
            self._errors['Output Field mapping:'] = self.error_class([
                'Incorrect list format. Please follow: ["your_column1","your_column2"]'])
            # self.add_error('output_field_mapping',
            #                'Incorrect list format. Please follow: ["your_column1","your_column2"]')
        try:
            ips = []
            for server in servers.split('|'):
                parts = server.split(':')
                if '-' in parts[2]:
                    threads, perssistance = parts[2].split('-')
                else:
                    threads = parts[2]
                if not re.match('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}', parts[1]) or not re.match('^\d+$',
                                                                                                               threads):
                    if parts[0] not in ips:
                        ips.append(parts[0])
            if ips:
                self._errors['Servers: '] = self.error_class([
                    'Incorrect server format for ' + ' '.join(ips)])
                # self.add_error('servers',
                #                'Incorrect server format for '+' '.join(ips))

        except:
            self._errors['Servers :'] = self.error_class([
                'Incorrect servers format.'])
            # self.add_error('servers',
            #                'Incorrect server format')
            # return any errors if found
        return self.cleaned_data
    class Meta:
        model = db_script
        widgets = {'user_id': forms.HiddenInput(), 'team': forms.HiddenInput(), 'servers': forms.Textarea(), 'input_field_mapping': forms.Textarea(), 'output_field_mapping': forms.Textarea()}
        fields = ('user_id', 'team',  'supplier_name',  'script_file', 'proxy_file', 'servers', 'input_field_mapping', 'output_field_mapping', 'timeout', 'attempt')


class db_batchForm(forms.ModelForm):
    # team = forms.CharField(max_length=30)
    # batch_name = forms.CharField(max_length=30)
    # input_file = forms.FileField()
    # script_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # proxies_file_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # server_file_name = forms.CharField(max_length=30)
    # region = forms.CharField(max_length=30)
    # scheduled_date = forms.DateField(required = True, input_formats=['%Y-%m-%d'])
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

        self.fields['region'].widget.attrs['class'] = "form-control"
        self.fields['region'].widget.attrs['required'] = ""
        self.fields['region'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please Enter the region code')"
        self.fields['region'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['input_file'].widget.attrs['class'] = "form-control"
        self.fields['input_file'].widget.attrs['required'] = ""
        self.fields['input_file'].widget.attrs['multiple'] = ""
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

        self.fields['frequency'].widget.attrs['name'] = "frequency"
        self.fields['frequency'].widget.attrs['id'] = "frequency"
        self.fields['frequency'].widget.attrs['value'] = "-1"



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
        widgets = {'user_id': forms.HiddenInput(), 'team': forms.HiddenInput(), 'frequency': forms.HiddenInput(),}
        fields = ('user_id', 'team',  'batch_name',  'region',  'input_file',  'script_name', 'scheduled_date', 'scheduled_time', 'frequency')


class db_edit_batchForm(forms.ModelForm):
    # team = forms.CharField(max_length=30)
    # batch_name = forms.CharField(max_length=30)
    # input_file = forms.FileField()
    # script_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # proxies_file_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # server_file_name = forms.CharField(max_length=30)
    # region = forms.CharField(max_length=30)
    # scheduled_date = forms.DateField(required = True, input_formats=['%Y-%m-%d'])
    def __init__(self, user_id, team, *args, **kwargs):
        super(db_edit_batchForm, self).__init__(*args, **kwargs)
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

        self.fields['region'].widget.attrs['class'] = "form-control"
        self.fields['region'].widget.attrs['required'] = ""
        self.fields['region'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please Enter the region code')"
        self.fields['region'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['input_file'].widget.attrs['class'] = "form-control"

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

        self.fields['frequency'].widget.attrs['type'] = "hidden"
        self.fields['frequency'].widget.attrs['name'] = "frequency"
        self.fields['frequency'].widget.attrs['value'] = "-2"


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
        fields = ('user_id', 'team',  'batch_name',  'region',  'input_file',  'script_name', 'scheduled_date', 'scheduled_time', 'frequency')


class db_edit_scriptForm(forms.ModelForm):
    # team = forms.CharField(max_length=30)
    # batch_name = forms.CharField(max_length=30)
    # input_file = forms.FileField()
    # script_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # proxies_file_name = forms.CharField(max_length=50, widget=forms.HiddenInput())
    # server_file_name = forms.CharField(max_length=30)
    # region = forms.CharField(max_length=30)

    def __init__(self, user_id, team, *args, **kwargs):
        super(db_edit_scriptForm, self).__init__(*args, **kwargs)
        # self.request = kwargs.pop('request', None)
        # super(MyForm, self).__init__(*args, **kwargs)

        # self.fields['user_id'].widget.attrs['type'] = "hidden"
        # self.fields['user_id'].widget.attrs.update({'type': 'hidden'})
        self.fields['user_id'].widget.attrs['value'] = user_id

        self.fields['team'].widget.attrs['value'] = team

        # self.fields['supplier_name'].widget.attrs['value'] = script_data["script_name"]
        self.fields['supplier_name'].widget.attrs['class'] = "form-control"
        self.fields['supplier_name'].widget.attrs['required'] = ""
        self.fields['supplier_name'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please Enter the supplier name')"
        self.fields['supplier_name'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        self.fields['script_file'].widget.attrs['class'] = "form-control"

        self.fields['proxy_file'].widget.attrs['class'] = "form-control"

        # self.fields['servers'].widget.attrs['value'] = script_data["servers"]
        self.fields['servers'].widget.attrs['class'] = "form-control"

        # self.fields['input_field_mapping'].widget.attrs['value'] = script_data["input_field_mapping"]
        self.fields['input_field_mapping'].widget.attrs['class'] = "form-control"
        self.fields['input_field_mapping'].widget.attrs['required'] = ""
        self.fields['input_field_mapping'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['input_field_mapping'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        # self.fields['output_field_mapping'].widget.attrs['value'] = script_data["output_field_mapping"]
        self.fields['output_field_mapping'].widget.attrs['class'] = "form-control"
        self.fields['output_field_mapping'].widget.attrs['required'] = ""
        self.fields['output_field_mapping'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['output_field_mapping'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        # self.fields['timeout'].widget.attrs['value'] = script_data["timeout"]
        self.fields['timeout'].widget.attrs['class'] = "form-control"
        self.fields['timeout'].widget.attrs['required'] = ""
        self.fields['timeout'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['timeout'].widget.attrs['oninput'] = "this.setCustomValidity('')"

        # self.fields['attempt'].widget.attrs['value'] = script_data["attempt"]
        self.fields['attempt'].widget.attrs['class'] = "form-control"
        self.fields['attempt'].widget.attrs['required'] = ""
        self.fields['attempt'].widget.attrs['oninvalid'] = "this.setCustomValidity('Please upload script')"
        self.fields['attempt'].widget.attrs['oninput'] = "this.setCustomValidity('')"


    def clean(self):
        print('validating script')
        super(db_edit_scriptForm, self).clean()
        input_field_mapping = self.cleaned_data.get('input_field_mapping')
        output_field_mapping = self.cleaned_data.get('output_field_mapping')
        servers = self.cleaned_data.get('servers')
        try:
            if not type(eval(input_field_mapping)) == type([]):
                self._errors['Input Field mapping:'] = self.error_class([
                    'Incorrect list format. Please follow: ["your_column1","your_column2"]'])
        except:
            self._errors['Input Field mapping:'] = self.error_class([
                'Incorrect list format. Please follow: ["your_column1","your_column2"]'])
            # self.add_error('input_field_mapping', 'Incorrect list format. Please follow: ["your_column1","your_column2"]')
            # raise ValidationError('Incorrect list format. Please follow: ["your_column1","your_column2"]')
        try:
            if not type(eval(output_field_mapping)) == type([]):
                self._errors['Output Field mapping:'] = self.error_class([
                    'Incorrect list format. Please follow: ["your_column1","your_column2"]'])
        except:
            self._errors['Output Field mapping:'] = self.error_class([
                'Incorrect list format. Please follow: ["your_column1","your_column2"]'])
            # self.add_error('output_field_mapping',
            #                'Incorrect list format. Please follow: ["your_column1","your_column2"]')
        try:
            ips = []
            for server in servers.split('|'):
                parts = server.split(':')
                if '-' in parts[2]:
                    threads, perssistance = parts[2].split('-')
                else:
                    threads = parts[2]
                if not re.match('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}', parts[1]) or not re.match('^\d+$', threads):
                    if parts[0] not in ips:
                        ips.append(parts[0])
            if ips:
                self._errors['Servers: '] = self.error_class([
                    'Incorrect server format for ' + ' '.join(ips)])
                # self.add_error('servers',
                #                'Incorrect server format for '+' '.join(ips))

        except:
            self._errors['Servers :'] = self.error_class([
                'Incorrect servers format.'])
            # self.add_error('servers',
            #                'Incorrect server format')
            # return any errors if found
        return self.cleaned_data
    class Meta:
        model = db_script
        widgets = {'user_id': forms.HiddenInput(), 'team': forms.HiddenInput(), 'servers': forms.Textarea(), 'input_field_mapping': forms.Textarea(), 'output_field_mapping': forms.Textarea()}
        fields = ('user_id', 'team',  'supplier_name',  'script_file', 'proxy_file', 'servers', 'input_field_mapping', 'output_field_mapping', 'timeout', 'attempt')

class add_server(forms.Form):
    original_field = forms.CharField()
    extra_field_count = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop('extra', 0)

        super(add_server, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = extra_fields

        for index in range(int(extra_fields)):
            # generate extra fields in the number specified via extra_fields
            self.fields['extra_field_{index}'.format(index=index)] = \
                forms.CharField()