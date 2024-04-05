import django_filters
from .models import Sample

class SampleFilter(django_filters.FilterSet):
    class Meta:
        model = Sample
        fields = ['Sample_Type', 'Material_Type', 'User_ID']  # Add more fields as needed
