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
    box = tables.Column(accessor='storage_id.box', verbose_name='Box', empty_values=())
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
                  'shelf', 'rack', 'box', 'unit_type')
