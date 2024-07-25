from django.contrib import admin

# Register your models here.

# new
from .models import Sample, OrganismType, UserProfile, Choice, VariableLabelMapping, University, Room, StorageUnit, Shelf, Rack, Storage, SampleInsertType, PhysicalStatus
# sample
admin.site.register(Sample)
admin.site.register(OrganismType)
admin.site.register(PhysicalStatus)
admin.site.register(Choice)
admin.site.register(VariableLabelMapping)
admin.site.register(UserProfile)
admin.site.register(SampleInsertType)

# storage
admin.site.register(University)
admin.site.register(Room)
admin.site.register(StorageUnit)
admin.site.register(Shelf)
admin.site.register(Rack)
admin.site.register(Storage)



