import django_filters
from .models import Sample, Storage, OrganismType, University, Room, StorageUnit, Shelf, Rack, UserProfile, PhysicalStatus
from django import forms 
from django.db.models import F, Value
from django.db.models.functions import Concat


class SampleFilter(django_filters.FilterSet):
    organism_type_choices = OrganismType.objects.values_list('organism_type', 'organism_type')
    host_id_choices = Sample.objects.values_list('id', 'id')
    owner_choices = UserProfile.objects.values_list('user_short', 'user_short')
    status_physical_choices = PhysicalStatus.objects.values_list('name', 'name')
    # Sample fields
    labnb_pgno = django_filters.CharFilter(lookup_expr='icontains', label='Lab Number')
    label_note = django_filters.CharFilter(lookup_expr='icontains', label='Label Note')
    organism_type = django_filters.ChoiceFilter(field_name='organism_type__organism_type', choices=organism_type_choices, label='Organism Type')
    material_type = django_filters.CharFilter(lookup_expr='icontains', label='Material Type')
    host_species = django_filters.CharFilter(lookup_expr='icontains', label='Host Species')
    host_strain = django_filters.CharFilter(lookup_expr='icontains', label='Host Strain')
    host_id = django_filters.ChoiceFilter(field_name='host_id', choices=host_id_choices, label='Host ID')
    storage_solution = django_filters.CharFilter(lookup_expr='icontains', label='Storage Solution')
    lab_lotno = django_filters.CharFilter(lookup_expr='icontains', label='Lab Lot Number')
    owner = django_filters.ChoiceFilter(field_name='owner__user_short', choices = owner_choices, label='Owner User Short')
    is_sequenced = django_filters.BooleanFilter(label='Is Sequenced')
    parent_name = django_filters.CharFilter(lookup_expr='icontains', label='Parent Name')
    general_comments = django_filters.CharFilter(lookup_expr='icontains', label='General Comments')
    genetic_modifications = django_filters.CharFilter(lookup_expr='icontains', label='Genetic Modifications')
    species = django_filters.CharFilter(lookup_expr='icontains', label='Species')
    strainname_main = django_filters.CharFilter(lookup_expr='icontains', label='Strain Name Main')
    strainname_core = django_filters.CharFilter(lookup_expr='icontains', label='Strain Name Core')
    strainname_other = django_filters.CharFilter(lookup_expr='icontains', label='Strain Name Other')
    strainname_atcc = django_filters.CharFilter(lookup_expr='icontains', label='Strain Name ATCC')
    strain_link = django_filters.CharFilter(lookup_expr='icontains', label='Strain Link')
    source_name = django_filters.CharFilter(lookup_expr='icontains', label='Source Name')
    is_purchased = django_filters.BooleanFilter(label='Is Purchased')
    source_lotno = django_filters.CharFilter(lookup_expr='icontains', label='Source Lot Number')
    is_undermta = django_filters.BooleanFilter(label='Is Under MTA')
    source_recommendedmedia = django_filters.CharFilter(lookup_expr='icontains', label='Source Recommended Media')
    tag = django_filters.CharFilter(lookup_expr='icontains', label='Tag')
    status_contamination = django_filters.CharFilter(lookup_expr='icontains', label='Contamination Status')
    status_QC = django_filters.CharFilter(lookup_expr='icontains', label='QC Status')
    status_physical = django_filters.ChoiceFilter(field_name='status_physical__name', choices=status_physical_choices, label='Physical Status')
    shared_with = django_filters.CharFilter(lookup_expr='icontains', label='Shared With')
    is_protected = django_filters.BooleanFilter(label='Is Protected')
    sequencing_infos = django_filters.CharFilter(lookup_expr='icontains', label='Sequencing Infos')
    plasmids = django_filters.CharFilter(lookup_expr='icontains', label='Plasmids')
    antibiotics = django_filters.CharFilter(lookup_expr='icontains', label='Antibiotics')

    # Storage choices
    university_name_choices = University.objects.values_list('university_name', 'university_name')
    room_number_choices = Room.objects.values_list('room_number', 'room_number')
    storage_unit_choices = StorageUnit.objects.values_list('storage_unit', 'storage_unit')
    shelf_choices = Shelf.objects.values_list('id', 'shelf')
    rack_choices = Rack.objects.values_list('id', 'rack')
    # shelf_choices = [(shelf.id, str(shelf)) for shelf in Shelf.objects.all()]
    # rack_choices = [(rack.id, str(rack)) for rack in Rack.objects.all()]

    university_name = django_filters.ChoiceFilter(field_name='storage_id__university_name__university_name', choices=university_name_choices, label='University Name')
    room_number = django_filters.ChoiceFilter(field_name='storage_id__room_number__room_number', choices = room_number_choices, label='Room Number')
    storage_unit = django_filters.ChoiceFilter(field_name='storage_id__storage_unit__storage_unit', choices = storage_unit_choices, label='Storage Unit')
    shelf = django_filters.ChoiceFilter(field_name='storage_id__shelf__shelf', choices = shelf_choices, label='Shelf')
    rack = django_filters.ChoiceFilter(field_name='storage_id__rack__rack', choices = rack_choices, label='Rack')
    box = django_filters.CharFilter(field_name='storage_id__box', lookup_expr='icontains', label='Box')

    unit_type = django_filters.CharFilter(field_name='storage_id__unit_type', lookup_expr='icontains', label='Unit Type')

    class Meta:
        model = Sample
        fields = []

    @property
    def form(self):
        form = super(SampleFilter, self).form
        for field_name in form.fields:
            classes = 'form-control'
            if isinstance(form.fields[field_name], forms.ChoiceField):
                classes = 'form-select'
            form.fields[field_name].widget.attrs.update({
                'class': classes,
                'style': 'max-width: 200px;'  # Adjust width as needed
            })
        return form

