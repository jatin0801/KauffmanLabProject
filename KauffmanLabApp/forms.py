from typing import Any
from django import forms
from django.apps import apps
import datetime
# from django.forms import ModelForm
from .models import VariableLabelMapping, UserProfile, University
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError      


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='', widget=forms.FileInput(attrs={'class': "form-control"}))

    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']
        if not file.name.endswith('.xlsx') and not file.name.endswith('.xls'):
            raise ValidationError('The uploaded file is not a valid Excel file. Please upload an .xls or .xlsx file.')
        return file
        

class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.form_group = kwargs.pop('form_group', None)
        self.filter_kwargs = kwargs.pop('filter_kwargs', None)
        self.initial_values = kwargs.pop('initial_values', None)
        super(DynamicForm, self).__init__(*args, **kwargs)
        if self.form_group:
            mappings = VariableLabelMapping.objects.filter(form_group=self.form_group).order_by('order_no')
            for mapping in mappings:
                # print(mapping.label_name, self.initial_values[mapping.variable_name], type(self.initial_values[mapping.variable_name]))
                field_kwargs = {
                    'label': mapping.label_name,
                    'required': mapping.field_required,
                    'initial': self.initial_values[mapping.variable_name] if self.initial_values else None,
                    'help_text': f'Prefix: {str(datetime.datetime.now().year)[-2:]}.{datetime.datetime.now().timetuple().tm_yday}' if mapping.variable_name == 'id' or mapping.variable_name == 'start_id' or mapping.variable_name == 'end_id'  else mapping.help_text,
                }
                if mapping.choice_table:
                    model_name = mapping.choice_table
                    app_label = 'KauffmanLabApp'
                    model = apps.get_model(app_label, model_name)
                    if self.filter_kwargs:
                        choices = [(getattr(choice, mapping.choice_id_field), getattr(choice, mapping.choice_text_field)) for choice in model.objects.filter(**self.filter_kwargs)]
                    else:
                        choices = [(getattr(choice, mapping.choice_id_field), getattr(choice, mapping.choice_text_field)) for choice in model.objects.all()]
                elif mapping.choices:
                    choices = [(choice.id, choice.choice_text) for choice in mapping.choices.all()]
                if mapping.field_type == 'char':
                    self.fields[mapping.variable_name] = forms.CharField(
                        **field_kwargs, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'})
                    )
                elif mapping.field_type == 'select':
                    # choices = [(choice.id, choice.choice_text) for choice in mapping.choices.all()]
                    self.fields[mapping.variable_name] = forms.ChoiceField(
                        **field_kwargs, choices=choices, widget=forms.Select(attrs={'class': 'form-select'})
                    )
                elif mapping.field_type == 'boolean':
                    self.fields[mapping.variable_name] = forms.BooleanField(
                        **field_kwargs, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                    )
                elif mapping.field_type == 'integer':
                    self.fields[mapping.variable_name] = forms.IntegerField(
                        **field_kwargs, widget=forms.NumberInput(attrs={'class': 'form-control'})
                    )
                elif mapping.field_type == 'email':
                    self.fields[mapping.variable_name] = forms.EmailField(
                        **field_kwargs, widget=forms.EmailInput(attrs={'class': 'form-control'})
                    )
                elif mapping.field_type == 'file':
                    self.fields[mapping.variable_name] = forms.FileField(
                        **field_kwargs, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
                    )
                elif mapping.field_type == 'url':
                    self.fields[mapping.variable_name] = forms.URLField(
                        **field_kwargs, widget=forms.URLInput(attrs={'class': 'form-control'})
                    )
                elif mapping.field_type == 'typedchoice':
                    self.fields[mapping.variable_name] = forms.TypedChoiceField(
                        **field_kwargs, choices=choices, coerce=int, widget=forms.Select(attrs={'class': 'form-control'})
                    )
                elif mapping.field_type == 'multiplechoice':
                    # choices = [(choice.id, choice.choice_text) for choice in mapping.choices.all()]
                    self.fields[mapping.variable_name] = forms.MultipleChoiceField(
                        **field_kwargs, choices=choices, widget=forms.SelectMultiple(attrs={'class': 'form-control'})
                    )
                elif mapping.field_type == 'typedmultiplechoice':
                    # choices = [(choice.id, choice.choice_text) for choice in mapping.choices.all()]
                    self.fields[mapping.variable_name] = forms.TypedMultipleChoiceField(
                        **field_kwargs, choices=choices, coerce=int, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
                    )

class UserRegistrationForm(forms.ModelForm):
    # form_group = 'user_register'
    # form = DynamicForm(form_group=form_group)
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    user_short = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'class': 'form-control'}))
    university_name = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select'}))
    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'university_name', 'user_short']
    
    def __init__(self, *args, **kwargs):
            super(UserRegistrationForm, self).__init__(*args, **kwargs)
            # self.dynamic_form = DynamicForm(*args, **kwargs)
            self.fields['university_name'].choices = [(university.id, university.university_name) for university in University.objects.all()]

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email']
        )
        user_profile = UserProfile(
            auth_user=user,
            university_name=self.cleaned_data['university_name'],
            user_short=self.cleaned_data['user_short']
        )
        if commit:
            user.save()
            user_profile.save()
        return user_profile
    
class ConfirmationForm(forms.Form):
    confirm = forms.BooleanField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, *args, **kwargs):
        confirm_message = kwargs.pop('confirm_message', 'Are you sure you want to perform this action?')
        super().__init__(*args, **kwargs)
        # self.fields['confirm'].label = confirm_message
        self.confirm_message = confirm_message