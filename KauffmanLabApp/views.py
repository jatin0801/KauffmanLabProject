from django.shortcuts import render, redirect, get_object_or_404
import re
import datetime
from django.http import HttpResponse, HttpResponseRedirect 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Sample, Storage, VariableLabelMapping, OrganismType, University, Room, StorageUnit, Shelf, Rack
from django.db.models import ForeignKey
from django.apps import apps
from .tables import SampleStorageTable
from .filters import SampleFilter
from .forms import DynamicForm, ConfirmationForm, UserRegistrationForm, ExcelUploadForm
import csv
import pandas as pd
from itertools import chain

# Export csv/pdf stuff
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Pagination stuff
from django.core.paginator import Paginator

from django.db.models import Prefetch, Subquery, F


def generate_sample_id(user_id, material_type, tube_id): #make tube_id 3 digit no
    current_year = datetime.datetime.now().strftime('%y')
    ordinal_day = datetime.datetime.now().timetuple().tm_yday
    ordinal_day_formatted = str(ordinal_day).zfill(3)
    tube_id = str(tube_id).zfill(3)
    identifier = f"{current_year}{ordinal_day_formatted}.{user_id}.{material_type}{tube_id}"
    return identifier

def home(request):
    session_data = list(VariableLabelMapping.objects.values_list('variable_name', flat=True))
    for s in session_data:
        if s in request.session:
            del request.session[s]
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
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = UserRegistrationForm()
    return render(request, 'KauffmanLabApp/register_user.html', {'form': form})

# TODO: Sample Edit function
@login_required
def sample_edit(request, sample_id):
    print("IN SAMPLE EDIT")
    sample = get_object_or_404(Sample, id=sample_id)
    initial_values = {field.name: getattr(sample, field.name) for field in sample._meta.fields}
    form_group = 'sample_form'    
    # set initial_values and send it to form
    if request.method == 'GET':
        form = DynamicForm(form_group=form_group, initial_values = initial_values)
        form_header = f'Editing Sample {sample_id}'
        return render(request, 'KauffmanLabApp/form.html', {'form': form, 'form_group': form_group, 'form_header': form_header})
    else:
        form = DynamicForm(request.POST, request.FILES, form_group=form_group)
        data = {}
        mappings = VariableLabelMapping.objects.filter(form_group=form_group).order_by('order_no')
        if form.is_valid():
            for m in mappings:
                data[m.variable_name] = form.cleaned_data.get(m.variable_name)
            data['id'] = sample.id
            save_sample(data, 'single')
            messages.success(request, f'Sample {sample.id} is updated successfully!')
        else:
            messages.warning(request, 'Update failed.')
        return redirect('sample_detail', pk=sample.id)

def sample_discard(request, sample_id):
    print("IN SAMPLE DELETE")
    sample = get_object_or_404(Sample, id=sample_id)
    if request.method == 'POST':
        form = ConfirmationForm(request.POST, confirm_message=f'Are you sure you want to discard sample {sample.id}?')
        if form.is_valid():
            if form.cleaned_data['confirm']:
                sample.is_discarded = True
                sample.save()
                messages.success(request, f'Sample {sample.id} discarded!')
                return redirect('sample_list')  # Replace 'sample_list' with your actual view name
            else:
                return redirect('sample_detail', pk=sample.id)
    else:
        form = ConfirmationForm(request.POST, confirm_message=f'Are you sure you want to discard sample {sample.id}?')
    return render(request, 'KauffmanLabApp/confirmation_page.html', {'form': form, 'sample': sample})

# TODO: diplay values from storage table. filters working fine.
@login_required
def sample_list(request):
    sample_filter = SampleFilter(request.GET, queryset=Sample.objects.all().order_by('id'))
    samples = sample_filter.qs
    # pagination
    p = Paginator(samples, 15)
    page = request.GET.get('page')
    samples = p.get_page(page)
    table = SampleStorageTable(samples)
    num_pgs = range(1, samples.paginator.num_pages + 1)

    query_params = request.GET.copy()
    query_params.pop('page', None)  # Remove the 'page' parameter if present
    query_string = query_params.urlencode()
    return render(request, 'KauffmanLabApp/sample_list.html', {'sample_filter': sample_filter, 'table': table, 'samples': samples, 'num_pgs':num_pgs, 'query_params': query_string})

# TODO: Export samples selected on multiple pages
def sample_csv(request):
    selections = request.GET.getlist('selection')
    print('selections', selections)
    sample_filter = SampleFilter(request.GET, queryset=Sample.objects.all())

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="samples.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Lab NB Page No', 'Label Note', 'Organism Type', 'Material Type', 'Status',
        'Storage Solution', 'Lab Lot No', 'Owner', 'Benchling Link', 'Is Sequenced',
        'Parent Name', 'General Comments', 'Genetic Modifications', 'Species',
        'Strain Name Main', 'Strain Name Core', 'Strain Name Other', 'Strain Name ATCC',
        'Strain Link', 'Source Name', 'Is Purchased', 'Source Lot No', 'Is Under MTA',
        'Source Recommended Media', 'Is Discarded', 'University Name', 'Room Number', 'Storage Unit',
        'Shelf', 'Rack', 'Unit Type'
    ])

    if request.GET:
        selections = request.GET.getlist('selection')
        if selections:
            selected_samples = Sample.objects.filter(id__in=selections)
        else:
            selected_samples = sample_filter.qs
    else:
        selected_samples = Sample.objects.all()

    for sample in selected_samples:
        writer.writerow([
            sample.id,
            sample.labnb_pgno,
            sample.label_note,
            sample.organism_type,
            sample.material_type,
            sample.status,
            sample.storage_solution,
            sample.lab_lotno,
            sample.owner,
            sample.benchling_link,
            sample.is_sequenced,
            sample.parent_name,
            sample.general_comments,
            sample.genetic_modifications,
            sample.species,
            sample.strainname_main,
            sample.strainname_core,
            sample.strainname_other,
            sample.strainname_atcc,
            sample.strain_link,
            sample.source_name,
            sample.is_purchased,
            sample.source_lotno,
            sample.is_undermta,
            sample.source_recommendedmedia,
            sample.is_discarded,
            sample.storage_id.university_name.university_name if sample.storage_id and sample.storage_id.university_name else '',
            sample.storage_id.room_number.room_number if sample.storage_id and sample.storage_id.room_number else '',
            sample.storage_id.storage_unit.storage_unit if sample.storage_id and sample.storage_id.storage_unit else '',
            sample.storage_id.shelf.shelf if sample.storage_id and sample.storage_id.shelf else '',
            sample.storage_id.rack.rack if sample.storage_id and sample.storage_id.rack else '',
            sample.storage_id.unit_type if sample.storage_id else '',
        ])

    return response

def sample_detail(request, pk):
    sample = get_object_or_404(Sample, pk=pk)
    column_mapping = {
        "ID": sample.id,
        "Lab NB Page Number": sample.labnb_pgno,
        "Label Note": sample.label_note,
        "Organism Type": sample.organism_type,
        "Material Type": sample.material_type,
        "Status": sample.status,
        "Storage Solution": sample.storage_solution,
        "Lab Lot Number": sample.lab_lotno,
        "Owner": sample.owner,
        "Benchling Link": sample.benchling_link,
        "Is Sequenced": sample.is_sequenced,
        "Parent Name": sample.parent_name,
        "General Comments": sample.general_comments,
        "Genetic Modifications": sample.genetic_modifications,
        "Species": sample.species,
        "Strain Name (Main)": sample.strainname_main,
        "Strain Name (Core)": sample.strainname_core,
        "Strain Name (Other)": sample.strainname_other,
        "Strain Name (ATCC)": sample.strainname_atcc,
        "Strain Link": sample.strain_link,
        "Source Name": sample.source_name,
        "Is Purchased": sample.is_purchased,
        "Source Lot Number": sample.source_lotno,
        "Is Under MTA": sample.is_undermta,
        "Source Recommended Media": sample.source_recommendedmedia,
        "Storage ID": sample.storage_id,
    }

    storage = sample.storage_id

    # Create a dictionary with storage data if storage is not None
    storage_mapping = {}
    if storage:
        storage_mapping = {
            "University Name": storage.university_name,
            "Room Number": storage.room_number,
            "Storage Unit": storage.storage_unit,
            "Shelf": storage.shelf,
            "Rack": storage.rack,
            "Unit Type": storage.unit_type,
        }
      
    # storage_details = get_object_or_404(Storage, Sample_ID_id=pk)
    return render(request, 'KauffmanLabApp/sample_detail.html', {'sample': sample, 'column_mapping': column_mapping, 'storage_mapping': storage_mapping,})

def display_alert(request, alert_type=None, alert_msg=None):
    return render(request, 'KauffmanLabApp/alerts.html', {'alert_type': alert_type, 'alert_msg': alert_msg})

# TODO: modify it as per new DB
def sample_pdf(request, selected_items = None):
    # Create a Django HTTP response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="samples.pdf"'

    # Create a PDF using SimpleDocTemplate in landscape mode
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # Data for the table
    data = [['Sample ID', 'Lab NB Page No', 'Label Note', 'Sample Type', 'Material Type', 'Parent Name', 'Source ID', 'User ID']]

    # Assuming Sample_Type and User_ID are foreign keys; adjust if not.
    if selected_items:
        samples = Sample.objects.filter(Sample_ID__in=selected_items).select_related('Sample_Type', 'User_ID')
    else:
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

# TODO: import from excel function
def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print('request.FILES', request.FILES)
            excel_file = request.FILES['excel_file']
            try:
                # Process the uploaded Excel file
                process_excel_file(excel_file)

                # Assuming the form contains only one file field named 'excel_file'
                messages.success(request, "File Uploaded Successfully")
            except Exception as e:
                messages.error(request, str(e))
            
            # return render(request, 'KauffmanLabApp/sample_list.html')
            return redirect('sample_list')
        else:
            print("Errors", form.errors)
            for _, error in form.errors.items():
                messages.error(request, error.as_text())
    else:
        form = ExcelUploadForm()
    return render(request, 'KauffmanLabApp/upload_excel.html', {'form': form})

# TODO: import from excel function
def process_excel_file(excel_file):
    # Define mapping of Excel column names to Django model field names
    column_mapping = {
        'Item Name *': 'Sample_ID',
        'labLog.nbPage': 'LabNB_PgNo',
        'labelNote.short': 'Label_Note',
        'Excel_Column_Name': 'Sample_Type',
        'materialType': 'Material_Type',
        'Excel_Column_Name': 'Parent_Name',
        # 'Excel_Column_Name': 'Source_ID', 
        # 'Excel_Column_Name': 'User_ID', extract form sample id
        'ATCC LINK': 'DigitalNB_Ref',
        # 'Excel_Column_Name': 'Original_Label',
        'Additional comment': 'Comments',
        # Add more mappings as needed
    }

    # Read Excel file into a DataFrame
    df = pd.read_excel(excel_file)

    # Iterate over rows and import data into the database
    for index, row in df.iterrows():
        sample_data = {}
        for excel_column, model_field in column_mapping.items():
            sample_data[model_field] = row[excel_column]

        # Create or update Sample object
        sample_id = sample_data.pop('Sample_ID')  # Assuming Sample_ID is a required field
        sample, created = Sample.objects.update_or_create(Sample_ID=sample_id, defaults=sample_data)

        # additional operations if needed

    print("Import completed successfully.")

def form_view(request, form_group):
    print('+++++++++++++++++form_group', request, form_group)
    form_group_mapping = {
        # 'sample_insert_type': {
        #     'keys': 'entry_type',
        #     'next': lambda request.session[key]: 'sample_insert_single' if request.session[key] == '1' else 'sample_insert_bulk'
        # },
        'sample_insert_single': {
            'key': 'id',
            'next': 'sample_form'
        },
        'sample_insert_bulk': {
            'keys': ['start_id', 'end_id'],
            'next': 'sample_form'
        },
        # 'sample_form': {
        #     'keys': [],  # Handled separately
        #     'next': '/'
        # },
        'storage_samples': {
            'key': 'sample_list',
            'next': 'storage_university'
        },
        'storage_university': {
            'key': 'university_name',
            'next': 'storage_room'
        },
        'storage_room': {
            'key': 'room_number',
            'next': 'storage_unit'
        },
        'storage_unit': {
            'key': 'storage_unit',
            'next': 'storage_shelf'
        },
        'storage_shelf': {
            'key': 'shelf',
            'next': 'storage_rack'
        },
        'storage_rack': {
            'key': 'rack',
            'next': 'storage_unit_type'
        },
        # 'storage_unit_type':{
        #     'key': 'unit_type',
        #     'next': '/'
        # }
    }
    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES, form_group=form_group)
        if form.is_valid():
            if form_group in form_group_mapping:
                mapping = form_group_mapping[form_group]
                keys = mapping.get('keys', [])
                if keys:
                    for key in keys:
                        request.session[key] = form.cleaned_data.get(key)
                else:
                    key = mapping['key']
                    request.session[key] = form.cleaned_data.get(key)
                next_form_group = mapping.get('next', '')
                return redirect('form_view', next_form_group)

        #=================+#
            if form_group=='sample_insert_type':
                entry_type = form.cleaned_data.get('entry_type')
                # single insert 
                if entry_type == '1':
                    form_group='sample_insert_single'
                    return redirect('form_view', form_group)
                # bulk insert 
                elif entry_type == '2':
                    form_group='sample_insert_bulk'
                    return redirect('form_view', form_group)

            elif form_group=='sample_form':
                data = {}
                mappings = VariableLabelMapping.objects.filter(form_group=form_group).order_by('order_no')
                for m in mappings:
                    data[m.variable_name] = form.cleaned_data.get(m.variable_name)
                if 'id' in request.session:
                    id = request.session.get('id', None)
                    data['id'] = id
                    save_sample(data, 'single')
                    messages.success(request, f'Sample {id} inserted successfuly')
                elif 'start_id' and 'end_id' in request.session:
                    start_id = request.session.get('start_id', None)
                    end_id = request.session.get('end_id', None)
                    data['start_id'] = start_id
                    data['end_id'] = end_id
                    save_sample(data, 'bulk')
                    messages.success(request, f'Samples {start_id} to {end_id} inserted successfuly')        
                return redirect('/')
            
            elif form_group=='storage_unit_type':
                unit_type = form.cleaned_data.get('unit_type')
                request.session['unit_type'] = unit_type
                save_storage(request)
                return redirect('/')
    else:
        filter_kwargs = None
        if form_group.startswith('storage_'):
            # Retrieve filter data from session for storage forms
            filter_kwargs = set_filtered_dropdown(request, form_group)
        form = DynamicForm(form_group=form_group, filter_kwargs = filter_kwargs)
    
    form_header = get_form_header(form_group)
    return render(request, 'KauffmanLabApp/form.html', {'form': form, 'form_group': form_group, 'form_header': form_header})

def set_filtered_dropdown(request, form_group):
    filter_kwargs = {}
    filter_column = {
        'storage_room': 'university_name',
        'storage_unit': 'room_number',
        'storage_shelf': 'storage_unit',
        'storage_rack': 'shelf'
    }.get(form_group, None)
    if filter_column:
        filter_data = request.session.get(filter_column)
        if filter_data:
            filter_kwargs = {filter_column: filter_data}
    return filter_kwargs

def get_form_header(form_group):
    form_header = ' '.join([part.title() for part in form_group.split('_')])
    return form_header

def save_sample(data, save_sample_type):

    # Handle organism_type
    if 'organism_type' in data:
        organism_type_value = data.pop('organism_type')
        try:
            organism_type_instance = OrganismType.objects.get(id=organism_type_value)
            data['organism_type'] = organism_type_instance
        except OrganismType.DoesNotExist:
            raise ValueError(f"OrganismType with value '{organism_type_value}' does not exist.")
        
    # Handle owner
    if 'owner' in data:
        owner_value = data.pop('owner')
        try:
            owner_instance = UserProfile.objects.get(auth_user__username=owner_value)
            data['owner'] = owner_instance
        except UserProfile.DoesNotExist:
            raise ValueError(f"UserProfile with username '{owner_value}' does not exist.")
    
    if save_sample_type == 'single':
        new_sample = Sample(**data)
        new_sample.save()
    
    if save_sample_type == 'bulk':
        start_id = data.pop('start_id')
        end_id = data.pop('end_id')
        sample_ids = get_bulk_sample_ids(start_id, end_id)
        for s in sample_ids:
            data['id'] = s
            new_sample = Sample(**data)
            new_sample.save()

def save_storage(request):
    model_fields = [field.name for field in Storage._meta.get_fields()]
    model_fields.remove('id')
    sample_list = request.session.get('sample_list')
    storage_data = {}
    fields_info = []
    for field in Storage._meta.get_fields():
        if isinstance(field, ForeignKey):
            fields_info.append({
                    'field_name': field.name,
                    'fk_model': field.related_model.__name__
                })
        storage_data[field.name] = request.session.get(field.name)
    for field_info in fields_info:
        field_name = field_info['field_name']
        if field_name in storage_data:
            fk_model = field_info['fk_model']
            app_label = 'KauffmanLabApp'
            fk_model = apps.get_model(app_label, fk_model)
            try:
                instance = fk_model.objects.get(id=storage_data[field_name])
                storage_data[field_name] = instance
            except fk_model.DoesNotExist:
                storage_data[field_name] = None

    for sample in sample_list:
        sample, created = Sample.objects.get_or_create(id=sample)
        if sample.storage_id:
            messages.warning(request, f'Sample {sample.id} already has a storage')
            continue
        storage = Storage(**storage_data)
        storage.save()
        sample.storage_id = storage
        sample.save()

def get_bulk_sample_ids(start_id, end_id):
    start = int(start_id.split('.')[-1])
    end = int(end_id.split('.')[-1])
    prefix_parts = end_id.split('.')[:-1]
    prefix = '.'.join(prefix_parts) + '.'
    sample_ids = [f"{prefix}{i:03d}" for i in range(start, end + 1)]
    return sample_ids