import django_tables2 as tables
from .models import Sample
from django_tables2.columns import CheckBoxColumn, Column

class SampleTable(tables.Table):
    selection = CheckBoxColumn(accessor='pk', orderable=False, empty_values=())  # add empty_values to avoid an error if no items selected
    fields = ['Sample_ID', 'LabNB_PgNo', 'Label_Note', 'Sample_Type', 'Material_Type', 'Parent_Name', 'Source_ID', 'User_ID', 'DigitalNB_Ref', 'Original_Label', 'Comments']
    Sample_ID = Column(attrs={'th': {'style': 'width: 100px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    LabNB_PgNo = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Label_Note = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Sample_Type = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Material_Type = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Parent_Name = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Source_ID = Column(attrs={'th': {'style': 'width: 250px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 250px;'}})
    User_ID = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    DigitalNB_Ref = Column(attrs={'th': {'style': 'width: 250px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 250px;'}})
    Original_Label = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Comments = Column(attrs={'th': {'style': 'width: 300px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 300px;'}})

    class Meta:
        model = Sample
        template_name = "django_tables2/bootstrap4.html" 
        attrs = {'class': 'table table-bordered'}
        fields = ['Sample_ID', 'LabNB_PgNo', 'Label_Note', 'Sample_Type', 'Material_Type', 'Parent_Name', 'Source_ID', 'User_ID', 'DigitalNB_Ref', 'Original_Label', 'Comments']
        sequence = ('selection',) + tuple(fields)
        attrs = {
            'class': 'table table-bordered',
            # 'thead': {'class': 'thead-light'},
            # 'th': {'class': 'align-middle'},
        }

    # Optionally, you can add more attributes to customize the appearance
    # selection.attrs.update({'th__input': {'class': 'select-all'}})  # add class to header checkbox for styling