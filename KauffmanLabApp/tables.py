import django_tables2 as tables
from .models import Sample
from django_tables2.columns import CheckBoxColumn, Column
from django_tables2.utils import A

# tables.py
import django_tables2 as tables
from .models import Sample, Storage

class SampleStorageTable(tables.Table):
    selection = CheckBoxColumn(accessor='pk', orderable=False, empty_values=())
    id = tables.Column(linkify=("sample_detail", {"pk": tables.A("id")}))
    labnb_pgno = tables.Column()
    label_note = tables.Column()
    organism_type = tables.Column()
    material_type = tables.Column()
    status = tables.Column()
    storage_solution = tables.Column()
    lab_lotno = tables.Column()
    owner = tables.Column()
    benchling_link = tables.Column()
    is_sequenced = tables.BooleanColumn()
    parent_name = tables.Column()
    general_comments = tables.Column()
    genetic_modifications = tables.Column()
    species = tables.Column()
    strainname_main = tables.Column()
    strainname_core = tables.Column()
    strainname_other = tables.Column()
    strainname_atcc = tables.Column()
    strain_link = tables.Column()
    source_name = tables.Column()
    is_purchased = tables.BooleanColumn()
    source_lotno = tables.Column()
    is_undermta = tables.BooleanColumn()
    source_recommendedmedia = tables.Column()
    is_discarded = tables.BooleanColumn()

    # Storage fields
    university_name = tables.Column(accessor='storage_id.university_name.university_name', verbose_name='University Name', empty_values=())
    room_number = tables.Column(accessor='storage_id.room_number.room_number', verbose_name='Room Number', empty_values=())
    storage_unit = tables.Column(accessor='storage_id.storage_unit.storage_unit', verbose_name='Storage Unit', empty_values=())
    shelf = tables.Column(accessor='storage_id.shelf.shelf', verbose_name='Shelf', empty_values=())
    rack = tables.Column(accessor='storage_id.rack.rack', verbose_name='Rack', empty_values=())
    unit_type = tables.Column(accessor='storage_id.unit_type', verbose_name='Unit Type', empty_values=())

    class Meta:
        model = Sample
        template_name = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered'}
        fields = ('selection', 'id', 'labnb_pgno', 'label_note', 'organism_type', 'material_type', 'status', 
                  'storage_solution', 'lab_lotno', 'owner', 'benchling_link', 'is_sequenced', 
                  'parent_name', 'general_comments', 'genetic_modifications', 'species', 
                  'strainname_main', 'strainname_core', 'strainname_other', 'strainname_atcc', 
                  'strain_link', 'source_name', 'is_purchased', 'source_lotno', 'is_undermta', 
                  'source_recommendedmedia', 'is_discarded', 'university_name', 'room_number', 'storage_unit', 
                  'shelf', 'rack', 'unit_type')

# Not used. Just keeping for reference
class SampleTable(tables.Table):
    selection = CheckBoxColumn(accessor='pk', orderable=False, empty_values=())  # add empty_values to avoid an error if no items selected
    Sample_ID = tables.Column(linkify=("sample_detail", {"pk": tables.A("Sample_ID")}), attrs={
        'th': {'style': 'width: 100px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'},
        'td': {'style': 'width: 100px;'}
    })

    # Create new Column instances for storage data
    university = Column(accessor='render_university', orderable=False, empty_values=(), attrs={
        'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'},
        'td': {'style': 'width: 100px;'}
    })
    room_number = Column(accessor='render_room_number', orderable=False, empty_values=(), attrs={
        'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'},
        'td': {'style': 'width: 100px;'}
    })
    storage_unit = Column(accessor='render_storage_unit', orderable=False, empty_values=(), attrs={
        'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'},
        'td': {'style': 'width: 100px;'}
    })
    shelf = Column(accessor='render_shelf', orderable=False, empty_values=(), attrs={
        'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'},
        'td': {'style': 'width: 100px;'}
    })
    rack = Column(accessor='render_rack', orderable=False, empty_values=(), attrs={
        'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'},
        'td': {'style': 'width: 100px;'}
    })
    unit_type = Column(accessor='render_unit_type', orderable=False, empty_values=(), attrs={
        'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'},
        'td': {'style': 'width: 100px;'}
    })
    
    # # Code for displaying storage data
    # university = tables.Column(empty_values=(), orderable=False)
    # room_number = tables.Column(empty_values=(), orderable=False)
    # storage_unit = tables.Column(empty_values=(), orderable=False)
    # shelf = tables.Column(empty_values=(), orderable=False)
    # rack = tables.Column(empty_values=(), orderable=False)
    # unit_type = tables.Column(empty_values=(), orderable=False)

    def render_university(self, record):
        if record.storage:
            return record.storage.University
        else:
            return '-'

    def render_room_number(self, record):
        if record.storage:
            return record.storage.Room_Number
        else:
            return '-'

    def render_storage_unit(self, record):
        if record.storage:
            return record.storage.Storage_Unit
        else:
            return '-'

    def render_shelf(self, record):
        if record.storage:
            return record.storage.Shelf
        else:
            return '-'

    def render_rack(self, record):
        if record.storage:
            return record.storage.Rack
        else:
            return '-'

    def render_unit_type(self, record):
        if record.storage:
            return record.storage.Unit_Type
        else:
            return '-'
    
    fields = ['Sample_ID', 'LabNB_PgNo', 'Label_Note', 'Sample_Type', 'Material_Type', 'Parent_Name', 'Source_ID', 'User_ID', 'DigitalNB_Ref', 'Original_Label', 'Comments']
    # Sample_ID = Column(attrs={'th': {'style': 'width: 100px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    LabNB_PgNo = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Label_Note = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Sample_Type = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Material_Type = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Storage_Solution = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Parent_Name = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Source_ID = Column(attrs={'th': {'style': 'width: 250px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 250px;'}})
    User_ID = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    DigitalNB_Ref = Column(attrs={'th': {'style': 'width: 250px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 250px;'}})
    Original_Label = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    Comments = Column(attrs={'th': {'style': 'width: 300px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 300px;'}})

    # university = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    # room_number = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    # storage_unit = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    # shelf = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    # rack = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})
    # unit_type = Column(attrs={'th': {'style': 'width: 200px; text-align: center; background-color:#C9DEF0; vertical-align: middle;'}, 'td': {'style': 'width: 100px;'}})

    class Meta:
        model = Sample
        template_name = "django_tables2/bootstrap4.html" 
        attrs = {'class': 'table table-bordered'}
        # fields = ['Sample_ID', 'LabNB_PgNo', 'Label_Note', 'Sample_Type', 'Material_Type', 'Storage_Solution', 'Parent_Name', 'Source_ID', 'User_ID', 'DigitalNB_Ref', 'Original_Label', 'Comments']
        fields = ['Sample_ID', 'LabNB_PgNo', 'Label_Note', 'Sample_Type', 'Material_Type', 'Storage_Solution', 'Parent_Name', 'Source_ID', 'User_ID', 'DigitalNB_Ref', 'Original_Label', 'Comments', 'university', 'room_number', 'storage_unit', 'shelf', 'rack', 'unit_type']
        sequence = ('selection',) + tuple(fields)
        # attrs = {
        #     'class': 'table table-bordered',
        #     'thead': {'class': 'thead-light'},
        #     'th': {'class': 'align-middle'},
        # }

    # Optionally, you can add more attributes to customize the appearance
    # selection.attrs.update({'th__input': {'class': 'select-all'}})  # add class to header checkbox for styling