from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User as AuthUser

# Create your models here.
class UserProfile(models.Model):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name='user_profile')
    University_Name = models.CharField(max_length=255)
    University_ID = models.CharField(max_length=255)
    User_Short = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.auth_user.username
    
@receiver(post_save, sender=AuthUser)  # Corrected sender
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(auth_user=instance)
    else:
        instance.user_profile.save()


class Sample_Types(models.Model):
    id = models.AutoField(primary_key=True)
    Sample_Type = models.CharField(max_length=255)

    def __str__(self):
        return self.Sample_Type

class Sample(models.Model):
    Sample_ID = models.CharField(max_length=255, primary_key=True)
    LabNB_PgNo = models.CharField(max_length=255)
    Label_Note = models.CharField(max_length=255)
    Sample_Type = models.ForeignKey(Sample_Types, blank=True, null=True, on_delete=models.SET_NULL)
    Material_Type = models.CharField(max_length=255)
    Parent_Name = models.CharField(max_length=255, blank=True, null=True)
    Source_ID = models.CharField(max_length=255, blank=True, null=True)
    User_ID = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)
    DigitalNB_Ref = models.CharField(max_length=255, blank=True, null=True)
    Original_Label = models.CharField(max_length=255, blank=True, null=True)
    Comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.Sample_ID
    
class Storage(models.Model):
    # Storage_ID = models.CharField(max_length=255, primary_key=True)
    Sample_ID = models.ForeignKey(Sample, on_delete=models.CASCADE)
    University = models.CharField(max_length=255)
    Room_Number = models.CharField(max_length=255)
    Tertiary_Storage_Type = models.CharField(max_length=255)
    Tertiary_Storage_ID = models.CharField(max_length=255)
    Secondary_Storage_Type = models.CharField(max_length=255, blank=True, null=True)
    Secondary_Storage_ID = models.CharField(max_length=255, blank=True, null=True)
    Primary_Storage_Type = models.CharField(max_length=255, blank=True, null=True)
    Primary_Storage_ID = models.CharField(max_length=255, blank=True, null=True)
    Unit_Type = models.CharField(max_length=255, blank=True, null=True)
    Storage_Solution = models.CharField(max_length=255, blank=True, null=True)
    Shelf = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.Sample_ID.Sample_ID

# Signal to create corresponding SampleType model for each Sample
@receiver(post_save, sender=Sample)
def create_sample_type(sender, instance, created, **kwargs):
    if created:
        # Access the Sample_Type's string representation or field directly
        sample_type_name = instance.Sample_Type.Sample_Type if instance.Sample_Type else None

        if sample_type_name == 'Bacteria':
            BacteriaSample.objects.create(Sample_ID=instance)
        elif sample_type_name == 'Virus':
            VirusSample.objects.create(Sample_ID=instance)
        elif sample_type_name == 'Environmental':
            EnvironmentalSample.objects.create(Sample_ID=instance)
        elif sample_type_name == 'Clinical':
            ClinicalSample.objects.create(Sample_ID=instance)

# Models for different Sample Types
class BacteriaSample(models.Model):
    Sample_ID = models.OneToOneField(Sample, on_delete=models.CASCADE, primary_key=True)
    Strain = models.CharField(max_length=255, blank=True, null=True)
    Species = models.CharField(max_length=255, blank=True, null=True)
    ATCC_ID = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.Sample_ID.Sample_ID
    
class VirusSample(models.Model):
    Sample_ID = models.OneToOneField(Sample, on_delete=models.CASCADE, primary_key=True)
    Strain = models.CharField(max_length=255, blank=True, null=True)
    Species = models.CharField(max_length=255, blank=True, null=True)
    ATCC_ID = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.Sample_ID.Sample_ID
    
class EnvironmentalSample(models.Model):
    Sample_ID = models.OneToOneField(Sample, on_delete=models.CASCADE, primary_key=True)
   
    def __str__(self):
        return self.Sample_ID.Sample_ID
    
class ClinicalSample(models.Model):
    Sample_ID = models.OneToOneField(Sample, on_delete=models.CASCADE, primary_key=True)
   
    def __str__(self):
        return self.Sample_ID.Sample_ID
