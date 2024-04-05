import django_tables2 as tables
from .models import Sample
from django_tables2.columns import CheckBoxColumn

class SampleTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor='pk', orderable=False)

    class Meta:
        model = Sample
        template_name = "django_tables2/bootstrap5.html" 