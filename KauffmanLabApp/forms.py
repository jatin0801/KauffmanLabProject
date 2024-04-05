from django import forms 
from django.forms import ModelForm
from .models import Sample
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create a Sample form
class SampleForm(forms.ModelForm):
    entry_type = forms.ChoiceField(choices=(('single', 'Single Entry'), ('batch', 'Batch Entry')), widget=forms.RadioSelect(), initial='single')
    tube_id = forms.CharField(label='Tube ID', widget=forms.TextInput(attrs={'class': "form-control", 'type': "text", 'placeholder': "eg. if 24040.EH1.GT006 then enter 006 or 6"}))
    tube_id_start = forms.CharField(label='Tube ID Start', widget=forms.TextInput(attrs={'class': "form-control", 'type': "text", 'placeholder': "eg. if 24040.EH1.GT006 then enter 006 or 6"}))
    tube_id_end = forms.CharField(label='Tube ID End', widget=forms.TextInput(attrs={'class': "form-control", 'type': "text", 'placeholder': "eg. if 24040.EH1.GT006 then enter 006 or 6"}))

    class Meta:
        model = Sample
        fields = ('entry_type', 'User_ID', 'Sample_Type', 'tube_id', 'tube_id_start', 'tube_id_end', 'LabNB_PgNo', 'Label_Note', 'Material_Type', 'Parent_Name', 'Source_ID', 'DigitalNB_Ref', 'Original_Label', 'Comments')
        exclude = ['Sample_ID']  # excluding Sample_ID as it's a primary key
        widgets = {
            'User_ID': forms.Select(attrs={'class': "form-select", 'id': "user_id", 'name': "user_id", 'required': True}),
            'Sample_Type': forms.Select(attrs={'class': "form-select", 'id': "sample_type", 'name': "sample_type", 'required': True}),
            'LabNB_PgNo': forms.TextInput(attrs={'class':"form-control", 'type':"text", 'id':"lab_pg_no", 'name':"lab_pg_no", 'placeholder':"Lab Page Number", 'aria-label':"default input example"}),
            'Label_Note': forms.TextInput(attrs={'class':"form-control", 'type':"text", 'id':"label_note", 'name':"label_note", 'placeholder':"Label Note", 'aria-label':"default input example"}),
            'Material_Type': forms.TextInput(attrs={'class':"form-control", 'type':"text", 'id':"material_type", 'name':"material_type", 'placeholder':"Material Type", 'aria-label':"default input example", 'required': True}),
            'Parent_Name': forms.TextInput(attrs={'class':"form-control", 'type':"text", 'id':"parent_name", 'name':"parent_name", 'placeholder':"Parent Name", 'aria-label':"default input example"}),
            'Source_ID': forms.TextInput(attrs={'class': "form-control", 'type': "text", 'id': "source_id", 'name': "source_id", 'placeholder': "Source ID", 'aria-label': "default input example"}),
            'DigitalNB_Ref': forms.TextInput(attrs={'class': "form-control", 'type': "text", 'id': "digitalnb_ref", 'name': "digitalnb_ref", 'placeholder': "Digital Notebook Reference", 'aria-label': "default input example"}),
            'Original_Label': forms.TextInput(attrs={'class': "form-control", 'type': "text", 'id': "original_label", 'name': "original_label", 'placeholder': "Original Label", 'aria-label': "default input example"}),
            'Comments': forms.TextInput(attrs={'class': "form-control", 'id': "comments", 'name': "comments", 'rows': "3"}),

        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['sample_type'].required = True  # Making sample_type required by default

        # Dynamically set required attribute based on entry_type
        # print("Entry type:", self.initial.get('entry_type'))  # Check the value of entry_type
        # if self.initial.get('entry_type') == 'single':
        #     print("Setting tube_id as required")
        #     self.fields['tube_id'].required = True
        #     self.fields['tube_id_start'].required = False
        #     self.fields['tube_id_end'].required = False
        # elif self.initial.get('entry_type') == 'batch':
        #     print("Setting tube_id_start and tube_id_end as required")
        #     self.fields['tube_id'].required = False
        #     self.fields['tube_id_start'].required = True
        #     self.fields['tube_id_end'].required = True

# tubeIdInput.setAttribute("required", "required");
# tubeIdStartInput.removeAttribute("required");
# tubeIdEndInput.removeAttribute("required");

# tubeIdInput.removeAttribute("required");
# tubeIdStartInput.setAttribute("required", "required");
# tubeIdEndInput.setAttribute("required", "required");
        

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')    
        

