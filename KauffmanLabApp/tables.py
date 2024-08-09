import django_tables2 as tables
from .models import Sample
from django_tables2.columns import CheckBoxColumn, Column
from django_tables2.utils import A

# tables.py
import django_tables2 as tables
from .models import Sample, Storage

class SampleStorageTable(tables.Table):
    selection = CheckBoxColumn(accessor='pk', orderable=False, empty_values=())
    id = tables.Column(linkify=("sample_detail", {"pk": tables.A("id")}), verbose_name='Unique ID')
    labnb_pgno = tables.Column(verbose_name='Lab Notebook Page')
    label_note = tables.Column(verbose_name='Label Note')
    organism_type = tables.Column(verbose_name='Organism Type')
    material_type = tables.Column(verbose_name='Material Type')
    host_species = tables.Column(verbose_name='Host Species')
    host_strain = tables.Column(verbose_name='Host Strain')
    host_id = tables.Column(verbose_name='Host ID')
    storage_solution = tables.Column(verbose_name='Storage Solution')
    lab_lotno = tables.Column(verbose_name='Lab Lot No.')
    owner = tables.Column(accessor='owner.user_short', verbose_name='Owner')
    benchling_link = tables.Column(verbose_name='Benchling Link')
    is_sequenced = tables.BooleanColumn(verbose_name='Is Sequenced')
    parent_name = tables.Column(verbose_name='Parent Name')
    general_comments = tables.Column(verbose_name='General Comments')
    genetic_modifications = tables.Column(verbose_name='Genetic Modifications')
    species = tables.Column(verbose_name='Species')
    strainname_main = tables.Column(verbose_name='Main Strain Name')
    strainname_core = tables.Column(verbose_name='Core Strain Name')
    strainname_other = tables.Column(verbose_name='Other Strain Name')
    strainname_atcc = tables.Column(verbose_name='ATCC Strain Name')
    strain_link = tables.Column(verbose_name='Strain Link')
    source_name = tables.Column(verbose_name='Source Name')
    is_purchased = tables.BooleanColumn(verbose_name='Is Purchased')
    source_lotno = tables.Column(verbose_name='Source Lot No.')
    is_undermta = tables.BooleanColumn(verbose_name='Is Under MTA')
    source_recommendedmedia = tables.Column(verbose_name='Source Recommended Media')
    tag = tables.Column(verbose_name='Tag')
    status_contamination = tables.Column(verbose_name='Contamination Status')
    status_QC = tables.Column(verbose_name='QC Status')
    status_physical = tables.Column(verbose_name='Physical Status')
    shared_with = tables.Column(verbose_name='Shared With')
    is_protected = tables.BooleanColumn(verbose_name='Is Protected')
    sequencing_infos = tables.Column(verbose_name='Sequencing Events')
    

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
        # attrs = {'class': 'table table-bordered'}
        fields = ('selection', 'id', 'labnb_pgno', 'label_note', 'organism_type', 'material_type', 
                  'host_species','host_strain', 'host_id',
                  'storage_solution', 'lab_lotno', 'owner', 'benchling_link', 'is_sequenced', 
                  'parent_name', 'general_comments', 'genetic_modifications', 'species', 
                  'strainname_main', 'strainname_core', 'strainname_other', 'strainname_atcc', 
                  'strain_link', 'source_name', 'is_purchased', 'source_lotno', 'is_undermta', 
                  'source_recommendedmedia', 'tag', 'status_contamination', 'status_QC', 'status_physical', 'shared_with', 'is_protected', 'sequencing_infos', 'university_name', 'room_number', 'storage_unit', 
                  'shelf', 'rack', 'box', 'unit_type')
