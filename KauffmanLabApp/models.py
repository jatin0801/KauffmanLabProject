from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone

# STORAGE
class University(models.Model):
    id = models.BigAutoField(primary_key=True)
    university_name = models.CharField(max_length=255)
    university_short = models.CharField(max_length=255)

    def __str__(self):
        return self.university_name

class Room(models.Model):
    id = models.BigAutoField(primary_key=True)
    room_number = models.CharField(max_length=255)
    university_name = models.ForeignKey(University, on_delete=models.CASCADE, related_name='rooms')

    def __str__(self):
        return f'{self.university_name} -> {self.room_number}'
    
class StorageUnit(models.Model):
    id = models.BigAutoField(primary_key=True)
    storage_unit = models.CharField(max_length=255)
    room_number = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='storage_units')

    def __str__(self):
        return f'{self.room_number} -> {self.storage_unit}'
    
class Shelf(models.Model):
    id = models.BigAutoField(primary_key=True)
    shelf = models.CharField(max_length=255)
    storage_unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE, related_name='shelves')

    def __str__(self):
        return f'{self.storage_unit} -> {self.shelf}'
    
class Rack(models.Model):
    id = models.BigAutoField(primary_key=True)
    rack = models.CharField(max_length=255)
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, related_name='racks')

    def __str__(self):
        return f'{self.shelf} -> {self.rack}'
    
class Storage(models.Model):
    id = models.BigAutoField(primary_key=True)
    university_name = models.ForeignKey(University, on_delete=models.CASCADE, related_name='storages')
    room_number = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='storages')
    storage_unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE, related_name='storages')
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, related_name='storages', null=True, blank=True)
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE, related_name='storages', null=True, blank=True)
    box = models.CharField(max_length=255, blank=True, null=True)
    unit_type = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
            return f'{self.rack} -> {self.unit_type}'

# SAMPLES
class OrganismType(models.Model):
    id = models.AutoField(primary_key=True)
    organism_type = models.CharField(max_length=255)

    def __str__(self):
        return self.organism_type
    
class PhysicalStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class SampleInsertType(models.Model):
    id = models.AutoField(primary_key=True)
    insert_type = models.CharField(max_length=255)

    def __str__(self):
        return self.insert_type

class UserProfile(models.Model):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name='user_profile')
    university_name = models.ForeignKey(University, on_delete=models.CASCADE, related_name='user_profile')
    user_short = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.auth_user.username

class Sample(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    labnb_pgno = models.CharField(max_length=255)
    label_note = models.CharField(max_length=255)
    organism_type = models.ForeignKey(OrganismType, blank=True, null=True, on_delete=models.SET_NULL)
    material_type = models.CharField(max_length=255)
    host_species = models.CharField(max_length=255, blank=True, null=True)
    host_strain = models.CharField(max_length=255, blank=True, null=True)
    host_id = models.CharField(max_length=255, blank=True, null=True)
    storage_solution = models.CharField(max_length=255, default='error')
    lab_lotno = models.CharField(max_length=255, default='error')
    owner = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)
    benchling_link = models.CharField(max_length=255, default='error')
    is_sequenced = models.BooleanField(blank=True, null=True)
    parent_name = models.CharField(max_length=255, blank=True, null=True)
    general_comments = models.TextField(blank=True, null=True)
    genetic_modifications = models.TextField(blank=True, null=True)
    species = models.CharField(max_length=255, blank=True, null=True)
    strainname_main = models.CharField(max_length=255, blank=True, null=True)
    strainname_core = models.CharField(max_length=255, blank=True, null=True)
    strainname_other = models.TextField(blank=True, null=True)
    strainname_atcc = models.CharField(max_length=255, blank=True, null=True)
    strain_link = models.CharField(max_length=255, blank=True, null=True)
    source_name = models.CharField(max_length=255, default='error')
    is_purchased = models.BooleanField(default=False, blank=True, null=True)
    source_lotno = models.CharField(max_length=255, default='error')
    is_undermta = models.BooleanField(blank=True, null=True)
    source_recommendedmedia = models.CharField(max_length=255, blank=True, null=True)
    tag = models.TextField(blank=True, null=True)
    status_contamination = models.CharField(max_length=255, blank=True, null=True)
    status_QC = models.TextField(blank=True, null=True)
    status_physical = models.ForeignKey(PhysicalStatus, blank=True, null=True, on_delete=models.SET_NULL)
    shared_with = models.TextField(blank=True, null=True)
    is_protected = models.BooleanField(default=False, blank=True, null=True)
    sequencing_infos = models.TextField(blank=True, null=True)
    plasmids = models.TextField(blank=True, null=True)
    antibiotics = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    storage_id = models.OneToOneField(Storage, null = True, on_delete = models.CASCADE)


    def __init__(self, *args, **kwargs):
        super(Sample, self).__init__(*args, **kwargs)
        for key, value in kwargs.items():
            print('Saving...', key, value)
            setattr(self, key, value)

    def __str__(self):
        return self.id

class Choice(models.Model):
    choice_text = models.CharField(max_length=100)

    def __str__(self):
        return self.choice_text
        
class VariableLabelMapping(models.Model):
    VARIABLE_TYPE_CHOICES = (
        ('char', 'CharField'),
        ('text', 'TextField'),
        ('select', 'SelectField'),
        ('boolean', 'BooleanField'),
        ('integer', 'IntegerField'),
        ('email', 'EmailField'),
        ('file', 'FileField'),
        ('url', 'URLField'),
        ('typedchoice', 'TypedChoiceField'),
        ('multiplechoice', 'MultipleChoiceField'),
        ('typedmultiplechoice', 'TypedMultipleChoiceField'),
        ('select2tag', 'Select2TagField'),
    )
    variable_name = models.CharField(max_length=100)
    label_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=25, choices=VARIABLE_TYPE_CHOICES)
    choices = models.ManyToManyField(Choice, blank=True)
    choice_table =  models.CharField(max_length=100, blank=True, null=True)
    choice_id_field = models.CharField(max_length=100, blank=True, null=True)
    choice_text_field =  models.CharField(max_length=100, blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    form_group = models.CharField(max_length=100)
    field_required = models.BooleanField(default=False)
    order_no = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.form_group} [{self.order_no}] -> {self.variable_name} ({self.get_field_type_display()})"
