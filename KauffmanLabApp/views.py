from django.shortcuts import render, redirect
import re
import datetime
import django_filters
from django.http import HttpResponse, HttpResponseRedirect 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Sample, Sample_Types
from .tables import SampleTable
from .filters import SampleFilter
from .forms import SampleForm, RegisterUserForm
import csv
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
# from django.contrib.auth.models import User

def generate_sample_id(user_id, material_type, tube_id): #make tube_id 3 digit no
    current_year = datetime.datetime.now().strftime('%y')
    ordinal_day = datetime.datetime.now().timetuple().tm_yday
    ordinal_day_formatted = str(ordinal_day).zfill(3)
    tube_id = str(tube_id).zfill(3)
    identifier = f"{current_year}{ordinal_day_formatted}.{user_id}.{material_type}{tube_id}"
    return identifier

def home(request):
    return render(request, "KauffmanLabApp/home.html")

def about(request):
    return render(request, "KauffmanLabApp/about.html")

def contact(request):
    return render(request, "KauffmanLabApp/contact.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Success you are logged in!")
            return redirect('/')
        else:
            messages.warning(request, "There was an error logging in. Try again!")
            return render(request, "KauffmanLabApp/login.html")

    else:
        return render(request, "KauffmanLabApp/login.html")
    
def user_logout(request):
    logout(request)
    messages.success(request, "Logout Successful!")
    return redirect('/')

def user_register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(user = username, password = password)
            login(request, user)
            messages.success(request, "Registeration Successful!")
            return redirect('/')
    else:
        form = RegisterUserForm()

    return render(request, "KauffmanLabApp/register_user.html", {'form': form})

@login_required
def sample_input(request):
    user_ids = UserProfile.objects.values_list('User_Short', flat=True).distinct()
    sample_types = Sample_Types.objects.values_list('Sample_Type', flat=True).distinct()
    return render(request, "KauffmanLabApp/sample_input.html", {'user_ids':user_ids, 'sample_types':sample_types})

def onSubmitSample(request):
    if request.method == 'POST':
        # Retrieve data from the form
        entry_type = request.POST.get('entry_type')
        user_short = request.POST.get('user_id')
        sample_type = request.POST.get('sample_type')
        material_type = request.POST.get('material_type')
        tube_id = request.POST.get('tube_id')
        tube_id_start = request.POST.get('tube_id_start')
        tube_id_end = request.POST.get('tube_id_end')
        lab_pg_no = request.POST.get('lab_pg_no')
        label_note = request.POST.get('label_note')
        parent_name = request.POST.get('parent_name')
        source_id = request.POST.get('source_id')
        digitalnb_ref = request.POST.get('digitalnb_ref')
        original_label = request.POST.get('original_label')
        comments = request.POST.get('comments')

        user_profile = UserProfile.objects.get(User_Short=user_short)
        # Access associated AuthUser and get the username
        user_id = user_profile.auth_user.id

        # Now you have all the form data captured, you can do further processing here
        if(entry_type=='single'):
            identifier = generate_sample_id(user_short, material_type, tube_id)
            print("identifier", identifier)
            sample_type_instance = Sample_Types.objects.get(Sample_Type=sample_type)
            new_sample = Sample(
            Sample_ID=identifier,
            LabNB_PgNo=lab_pg_no,
            Label_Note=label_note,
            Sample_Type=sample_type_instance,
            Material_Type=material_type,
            User_ID_id=user_id,
            Parent_Name = parent_name,
            Source_ID = source_id,
            DigitalNB_Ref = digitalnb_ref,
            Original_Label = original_label,
            Comments = comments
            )
            new_sample.save()
            messages.success(request, 'Sample saved successfully.')

        elif(entry_type == 'batch'):
            tube_id_start, tube_id_end = int(tube_id_start), int(tube_id_end)
            if(tube_id_start>0 and tube_id_end<=200 and tube_id_start<tube_id_end):
                identifiers = []
                for tube_id in range(tube_id_start, tube_id_end+1):
                    id = generate_sample_id(user_short, material_type, str(tube_id))
                    identifiers.append(id)
                    print('sample type', sample_type)
                    sample_type_instance = Sample_Types.objects.get(Sample_Type=sample_type)
                    print('sample sample_type_instance', sample_type_instance)
                    new_sample = Sample(
                    Sample_ID=id,
                    LabNB_PgNo=lab_pg_no,
                    Label_Note=label_note,
                    Sample_Type=sample_type_instance,
                    Material_Type=material_type,
                    User_ID_id=user_id,
                    Parent_Name = parent_name,
                    Source_ID = source_id,
                    DigitalNB_Ref = digitalnb_ref,
                    Original_Label = original_label,
                    Comments = comments
                    )
                    new_sample.save()
                print("identifiers", identifiers)
                messages.success(request, 'Sample saved successfully.')
                
            else:
                display_alert(request, 'danger', 'Error: Invalid input.')
                print("Error: Invalid input")
                messages.warning(request, 'Error: Invalid input.')
        
        print('Entry Type:', entry_type)
        print('User ID:', user_id)
        print('Sample Type:', sample_type)
        print('Material Type:', material_type)
        print('Tube ID:', tube_id)
        print('Tube ID Start:', tube_id_start)
        print('Tube ID End:', tube_id_end)
        print('Lab Page Number:', lab_pg_no)
        print('Label Note:', label_note)
        print('Parent_Name:', parent_name)
        print('Source_ID:', source_id)
        print('DigitalNB_Ref', digitalnb_ref)
        print('Original_Label', original_label)
        print('Comments', comments)


        # For this example, let's return a simple response
        return redirect('sample_input')
    else:
        # Handle GET requests or other methods here
        return render(request, 'sample_input.html')


@login_required  
def sample_list(request):
    sample_filter = SampleFilter(request.GET, queryset=Sample.objects.all())
    return render(request, 'KauffmanLabApp/sample_list.html', {'filter': sample_filter})

def sample_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename=samples.csv'

    # csv writer
    writer = csv.writer(response)

    samples = Sample.objects.all()

    #Add col headings of csv
    writer.writerow(['Sample ID', 'Lab NB Page No', 'Label Note', 'Sample Type', 'Material Type', 'Parent Name', 'Source ID', 'User ID', 'Digital NB Reference', 'Original Label', 'Comments'])

    #loop through samples
    for s in samples:
        writer.writerow([s.Sample_ID, s.LabNB_PgNo, s.Label_Note, s.Sample_Type, s.Material_Type, s.Parent_Name, s.Source_ID, s.User_ID, s.DigitalNB_Ref, s.Original_Label, s.Comments])

    return response

def display_alert(request, alert_type=None, alert_msg=None):
    return render(request, 'KauffmanLabApp/alerts.html', {'alert_type': alert_type, 'alert_msg': alert_msg})

def sample_pdf(request):
    # Create a Django HTTP response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="samples.pdf"'

    # Create a PDF using SimpleDocTemplate in landscape mode
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # Data for the table
    data = [['Sample ID', 'Lab NB Page No', 'Label Note', 'Sample Type', 'Material Type', 'Parent Name', 'Source ID', 'User ID']]

    # Assuming Sample_Type and User_ID are foreign keys; adjust if not.
    samples = Sample.objects.all().select_related('Sample_Type', 'User_ID')
    for s in samples:
        data.append([
            s.Sample_ID,
            s.LabNB_PgNo,
            s.Label_Note,
            str(s.Sample_Type) if s.Sample_Type else '',  # Ensure foreign key object exists
            s.Material_Type,
            s.Parent_Name,
            s.Source_ID,
            str(s.User_ID) if s.User_ID else '',  # Ensure foreign key object exists
            # s.DigitalNB_Ref,
            # s.Original_Label,
            # s.Comments
        ])

    # Create a table and add styles
    table = Table(data)
    table.setStyle(TableStyle([
       ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
       ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
       ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
       ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
       ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    # Adjust table column widths as needed here
    # table._argW[0] = desired width of each column, e.g., 1.2*inch
    # Assuming you have 11 columns from the data array
    # num_columns = len(data[0])
    # total_width = 10 * inch  # Approximate usable width
    # column_width = total_width / num_columns

    # Create a table and specify the width for each column
    # table = Table(data, colWidths=[column_width] * num_columns)
    # Build the PDF
    doc.build([table])
    return response




     