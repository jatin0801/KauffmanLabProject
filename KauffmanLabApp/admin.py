from django.contrib import admin

# Register your models here.
from .models import Sample
from .models import BacteriaSample
from .models import VirusSample
from .models import EnvironmentalSample
from .models import ClinicalSample
from .models import Storage
from .models import UserProfile
from .models import Sample_Types

admin.site.register(Sample)
admin.site.register(BacteriaSample)
admin.site.register(VirusSample)
admin.site.register(EnvironmentalSample)
admin.site.register(ClinicalSample)
admin.site.register(Storage)
admin.site.register(UserProfile)
admin.site.register(Sample_Types)



