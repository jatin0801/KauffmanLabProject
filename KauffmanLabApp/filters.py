import django_filters
from .models import Sample
from django import forms 

class SampleFilter(django_filters.FilterSet):
    class Meta:
        model = Sample
        fields = ['Sample_Type', 'Material_Type', 'User_ID', 'Parent_Name']  # Add more fields as needed
        widgets = {
            'Sample_Type': forms.Select(attrs={'class': "form-select", 'id': "sample_type", 'name': "user_sample_typeid", 'required': True}),
            'User_ID': forms.Select(attrs={'class': "form-select", 'id': "user_id", 'name': "user_id", 'required': True}),
            'Material_Type': forms.TextInput(attrs={'class': "form-control", 'type': "text", 'id': "material_type", 'name': "material_type", 'placeholder': "Material Type", 'aria-label': "default input example"}),
            'Parent_Name': forms.TextInput(attrs={'class': "form-control", 'type': "text", 'id': "parent_name", 'name': "parent_name", 'placeholder': "Parent Name", 'aria-label': "default input example"}),
        }