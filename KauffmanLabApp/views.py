from django.shortcuts import render, redirect, get_object_or_404
import re
import datetime
from django.http import HttpResponse, HttpResponseRedirect 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import UserProfile, Sample, Storage, VariableLabelMapping, OrganismType, University, Room, StorageUnit, Shelf, Rack, PhysicalStatus
from django.db.models import ForeignKey
from django.db import transaction
from django.apps import apps
from django_tables2 import RequestConfig
from .tables import SampleStorageTable
from .filters import SampleFilter
from .forms import DynamicForm, ConfirmationForm, UserRegistrationForm, ExcelUploadForm, SampleSearchForm

import csv
import pandas as pd
import numpy as np
from itertools import chain
import os
import tempfile
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import subprocess


# Export csv/pdf stuff
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

# Pagination stuff
from django.core.paginator import Paginator

from django.db.models import Prefetch, Subquery, F
from django.db.models import Q



def generate_sample_id(user_id, material_type, tube_id): #make tube_id 3 digit no
    current_year = datetime.datetime.now().strftime('%y')
    ordinal_day = datetime.datetime.now().timetuple().tm_yday
    ordinal_day_formatted = str(ordinal_day).zfill(3)
    tube_id = str(tube_id).zfill(3)
    identifier = f"{current_year}{ordinal_day_formatted}.{user_id}.{material_type}{tube_id}"
    return identifier

def home(request):
    clear_session_data(request)
    return render(request, "KauffmanLabApp/home.html")

def clear_session_data(request):
    session_data = list(VariableLabelMapping.objects.values_list('variable_name', flat=True))
    for s in session_data:
        if s in request.session:
            del request.session[s]
    request.session.save()

def about(request):
    return render(request, "KauffmanLabApp/about.html")

def admin_panel(request):
    clear_session_data(request)
    return render(request, "KauffmanLabApp/admin_panel.html")

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

@login_required
def user_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'KauffmanLabApp/change_password.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            # Create the User object
            user = User.objects.create_user(
                username=cleaned_data['username'],
                password=cleaned_data['password'],
                first_name=cleaned_data['first_name'],
                last_name=cleaned_data['last_name'],
                email=cleaned_data['email']
            )

            # Fetch the University instance
            # university_instance = University.objects.get(id=cleaned_data['university_name'])

            # Create the UserProfile object
            user_profile = UserProfile(
                auth_user=user,
                university_name=cleaned_data['university_name'],  # This is now a University instance
                user_short=cleaned_data['user_short']
            )

            # Save the user and user profile
            user.save()
            user_profile.save()

            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'KauffmanLabApp/register_user.html', {'form': form})

def handle_foreign_data(data, var, model, field='id'):
    if var in data and data[var] != '':
        var_value = data.pop(var)
        try:
            if field == 'id':
                var_instance = model.objects.get(id=var_value)
            elif field == 'first_last_name':
                first_name, last_name = var_value.split()
                var_instance = model.objects.get(
                    auth_user__first_name=first_name, auth_user__last_name=last_name
                )
            else:
                var_instance = model.objects.get(**{field: var_value})
            data[var] = var_instance
        except model.DoesNotExist:
            raise ValueError(f"{model.__name__} with value '{var_value}' does not exist.")
    return data

@user_passes_test(lambda u: u.is_staff)
def sample_edit(request, sample_id):
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
            #Handle foreign data
            data = handle_foreign_data(data, 'organism_type', OrganismType)
            data = handle_foreign_data(data, 'owner', UserProfile, field='auth_user__username')
            data = handle_foreign_data(data, 'status_physical', PhysicalStatus)
                
            data['id'] = sample.id
            sample_id = sample.id  # Assuming ID is a required field
            sample, created = Sample.objects.update_or_create(id=sample_id, defaults=data)
            messages.success(request, f'Sample {sample.id} is updated successfully!')
        else:
            messages.warning(request, 'Update failed.')
        return redirect('sample_detail', pk=sample.id)

# def sample_discard(request, sample_id):
#     sample = get_object_or_404(Sample, id=sample_id)
#     if request.method == 'POST':
#         form = ConfirmationForm(request.POST, confirm_message=f'Are you sure you want to discard sample {sample.id}?')
#         if form.is_valid():
#             if form.cleaned_data['confirm']:
#                 sample.is_discarded = True
#                 sample.save()
#                 messages.success(request, f'Sample {sample.id} discarded!')
#                 return redirect('sample_list')  # Replace 'sample_list' with your actual view name
#             else:
#                 messages.info(request, "Discard action cancelled.")
#                 return redirect('sample_detail', pk=sample.id)
#     else:
#         form = ConfirmationForm(request.POST, confirm_message=f'Are you sure you want to discard sample {sample.id}?')
#     return render(request, 'KauffmanLabApp/confirmation_page.html', {'form': form, 'sample': sample})

# TODO: always cancels deletion because of confirmation page
def sample_delete(request, sample_list):
    samples_to_delete = Sample.objects.filter(id__in=sample_list)
    # samples_to_delete_discarded = Sample.objects.filter(id__in=sample_list, is_discarded=True)
    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['confirm']:
                samples_to_delete.delete()
                messages.success(request, f"{len(sample_list)} discarded samples deleted successfully.")
                return redirect('sample_list')
            else:
                messages.info(request, "Deletion canceled.")
                return redirect('sample_list')  # Redirect or render another page if canceled
    else:
        samples_to_delete_ids = list(samples_to_delete.values_list('id', flat=True))
        # samples_to_delete_discarded_ids = list(samples_to_delete_discarded.values_list('id', flat=True))
        # samples_to_delete_not_discarded_ids = list(set(samples_to_delete_ids) - set(samples_to_delete_discarded_ids))

        # if samples_to_delete_not_discarded_ids:
        #     confirm_message = (
        #                     f"Are you sure you want to delete the samples?\n"
        #                     f"<br/> Actions:"
        #                     f"<ul>"
        #                     f"  <li>Delete Samples:<ul>{sample_list}</ul></li>"
        #                     f"  <li>Samples that are not discarded:<ul>{samples_to_delete_not_discarded_ids}</ul></li>"
        #                     f"</ul>"
        #                 )
        # else:
        confirm_message = (
                        f"Are you sure you want to delete the samples?\n"
                        f"<br/> Actions:"
                        f"<ul>"
                        f"  <li>Delete Samples:<ul>{samples_to_delete_ids}</ul></li>"
                        f"</ul>"
                    )
        form = ConfirmationForm(request.POST, confirm_message=confirm_message)

    return render(request, 'KauffmanLabApp/confirmation_page.html', {'form': form})

# TODO: diplay values from storage table. filters working fine.
@login_required
def sample_list(request, samples=None):
    if request.method == 'POST':
        selections = request.POST.getlist('selection')
        action = request.POST.get('action')    
        if action:
            sample_list = request.session.get('sample_list', [])
            
            if action == 'add_bulk_storage':
                if not sample_list and selections:
                    sample_list = selections              
                return add_bulk_storage(request, sample_list)
            
            elif action == 'export_csv':
                return export_excel_csv(request, sample_list, action)
            
            elif action == 'export_excel':
                return export_excel_csv(request, sample_list, action)
            
            elif action == 'save_selection':
                sample_list.extend(selections)
                sample_list=list(set(sample_list))
                request.session['sample_list'] = sample_list
                request.session.save()
                formatted_list = ', '.join(sample_list) if sample_list else 'None'
                messages.success(request, f'Selected samples: {formatted_list}')
            
            elif action == 'clear_selection':
                clear_session_data(request)
                messages.info(request, f'Sample selection cleared')
            
            elif action == 'sample_delete':
                if not sample_list and selections:
                    sample_list = selections              
                return sample_delete(request, sample_list)
            
            return redirect('sample_list')
        else:
            clear_session_data(request)
            
    
    # Get all samples
    if samples==None:
        samples = Sample.objects.all()

    # Handle search filtering
    search_query = request.GET.get('search')
    if search_query:
        samples = get_search_results(samples, search_query)
        
    # Handle sorting
    # sort_by_col = request.GET.get('sort', '-id')
    # field_names = [field.name for field in Sample._meta.get_fields()]
    # if sort_by_col in field_names:
    #     samples = samples.order_by('-'+sort_by_col)
    # else:
    #     messages.info(request, 'Sorry! I cannot sort by storage related field')
    #     samples = samples.order_by('-id')

    # Apply filters
    sample_filter = SampleFilter(request.GET, queryset=samples)
    samples = sample_filter.qs

    # sorting
    sort_by_col = request.GET.get('sort', 'created_at')
    current_order = request.GET.get('order', 'asc')

    foreign_key_sort_map = {
    'organism_type': 'organism_type__organism_type',
    'owner': 'owner__user_short', 
    'status_physical': 'status_physical__name',
    'storage_id.university_name.university_name': 'storage_id__university_name__university_name',
    'storage_id.room_number.room_number': 'storage_id__room_number__room_number',
    'storage_id.storage_unit.storage_unit': 'storage_id__storage_unit__storage_unit',
    'storage_id.shelf.shelf': 'storage_id__shelf__shelf',
    'storage_id.rack.rack': 'storage_id__rack__rack',
    'storage_id.box': 'storage_id__box',
    'storage_id.unit_type': 'storage_id__unit_type',
    }
    sort_by_col = foreign_key_sort_map.get(sort_by_col, sort_by_col)
    
    if current_order == 'asc':
        samples = samples.order_by(sort_by_col)
        new_order = 'desc'
    else:
        samples = samples.order_by('-' + sort_by_col)
        new_order = 'asc'

    # Pagination
    p = Paginator(samples, 250)
    page = request.GET.get('page')
    samples = p.get_page(page)
    table = SampleStorageTable(samples)
    num_pgs = range(1, samples.paginator.num_pages + 1)

    # Number of samples displayed on the current page
    num_samples_displayed = len(samples.object_list)
    num_samples_displayed = len(samples)
    total_samples = p.count
    start_sample = (samples.number - 1) * p.per_page + 1
    end_sample = min(samples.number * p.per_page, total_samples)
   
    table = SampleStorageTable(samples)
    num_samples_displayed = len(samples)
    # RequestConfig(request).configure(table)

    query_params = request.GET.copy()
    query_params.pop('page', None)  # Remove the 'page' parameter if present
    query_string = query_params.urlencode()            
    return render(request, 'KauffmanLabApp/sample_list.html', {
        'sample_filter': sample_filter,
        'table': table,
        'samples': samples,
        'num_pgs': num_pgs,
        'query_params': query_string,
        'search_form': SampleSearchForm(request.GET),
        'num_samples_displayed': num_samples_displayed,
        'new_order': new_order,
        'total_samples': total_samples,
        'start_sample': start_sample,
        'end_sample': end_sample,
    })

def get_search_results(samples, search_query):
    samples = samples.filter(
            Q(id__icontains=search_query) |
            Q(labnb_pgno__icontains=search_query) |
            Q(label_note__icontains=search_query) |
            Q(organism_type__organism_type__icontains=search_query) |
            Q(material_type__icontains=search_query) |
            Q(host_species__icontains=search_query) |
            Q(host_strain__icontains=search_query) |
            Q(host_id__icontains=search_query) |
            Q(storage_solution__icontains=search_query) |
            Q(lab_lotno__icontains=search_query) |
            Q(owner__auth_user__username__icontains=search_query) |
            Q(benchling_link__icontains=search_query) |
            Q(parent_name__icontains=search_query) |
            Q(general_comments__icontains=search_query) |
            Q(genetic_modifications__icontains=search_query) |
            Q(species__icontains=search_query) |
            Q(strainname_main__icontains=search_query) |
            Q(strainname_core__icontains=search_query) |
            Q(strainname_other__icontains=search_query) |
            Q(strainname_atcc__icontains=search_query) |
            Q(strain_link__icontains=search_query) |
            Q(source_name__icontains=search_query) |
            Q(source_lotno__icontains=search_query) |
            Q(source_recommendedmedia__icontains=search_query) |
            Q(tag__icontains=search_query) |
            Q(status_contamination__icontains=search_query) |
            Q(status_QC__icontains=search_query) |
            Q(status_physical__name__icontains=search_query) |
            Q(shared_with__icontains=search_query) |
            Q(is_protected__icontains=search_query) |
            Q(sequencing_infos__icontains=search_query) |
            Q(plasmids__icontains=search_query) |
            Q(antibiotics__icontains=search_query) |
            Q(storage_id__university_name__university_name__icontains=search_query) |
            Q(storage_id__room_number__room_number__icontains=search_query) |
            Q(storage_id__storage_unit__storage_unit__icontains=search_query) |
            Q(storage_id__shelf__shelf__icontains=search_query) |
            Q(storage_id__rack__rack__icontains=search_query) |
            Q(storage_id__box__icontains=search_query) |
            Q(storage_id__unit_type__icontains=search_query)
        )
    return samples

def export_excel_csv(request, selections=None, action='export_excel'):
    sample_filter = SampleFilter(request.GET, queryset=Sample.objects.all()) 
    
    if selections:
        samples = Sample.objects.filter(id__in=selections)
    else:
        if request.POST:
            selections = request.POST.getlist('selection')
            if selections:
                samples = Sample.objects.filter(id__in=selections)
            else:
                samples = sample_filter.qs
        else:
            samples = Sample.objects.all()

    now = datetime.datetime.now()
    timestamp = f"{str(now.year)[-2:]}{now.timetuple().tm_yday}_{now.strftime('%H%M%S')}"

    export_samples = []
    for sample in samples:
        export_samples.append(
            [sample.id,
            sample.labnb_pgno,
            sample.label_note,
            sample.organism_type.organism_type if sample.organism_type else '',
            sample.material_type,
            sample.host_species,
            sample.host_strain,
            sample.host_id,
            sample.storage_solution,
            sample.lab_lotno,
            sample.owner.user_short if sample.owner else '',
            sample.benchling_link,
            'Yes' if sample.is_sequenced else 'No',
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
            'Yes' if sample.is_purchased else 'No',
            sample.source_lotno,
            'Yes' if sample.is_undermta else 'No',
            sample.source_recommendedmedia,
            sample.tag,
            sample.status_contamination,
            sample.status_QC,
            sample.status_physical.name if sample.status_physical else '',
            sample.shared_with,
            'Yes' if sample.is_protected else 'No',
            sample.sequencing_infos,
            sample.plasmids,
            sample.antibiotics,
            sample.storage_id.university_name.university_name if sample.storage_id and sample.storage_id.university_name else '',
            sample.storage_id.room_number.room_number if sample.storage_id and sample.storage_id.room_number else '',
            sample.storage_id.storage_unit.storage_unit if sample.storage_id and sample.storage_id.storage_unit else '',
            sample.storage_id.shelf.shelf if sample.storage_id and sample.storage_id.shelf else '',
            sample.storage_id.rack.rack if sample.storage_id and sample.storage_id.rack else '',
            sample.storage_id.box if sample.storage_id else '',
            sample.storage_id.unit_type if sample.storage_id else ''
            ]
        )

    if action == 'export_csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{timestamp}.samples_backup.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Lab NB Page No', 'Label Note', 'Organism Type', 'Material Type',
            'Host Species', 'Host Strain', 'Host ID',
            'Storage Solution', 'Lab Lot No', 'Owner', 'Benchling Link', 'Is Sequenced',
            'Parent Name', 'General Comments', 'Genetic Modifications', 'Species',
            'Strain Name Main', 'Strain Name Core', 'Strain Name Other', 'Strain Name ATCC',
            'ATCC Link', 'Source Name', 'Is Purchased', 'Source Lot No', 'Is Under MTA',
            'Source Recommended Media', 'Tag', 'Contamination Status',	'QC Status', 'Physical Status',	'Shared With', 'Is Protected', 'Sequencing Infos',
            'Plasmids', 'Antibiotics',
            'University Name', 'Room Number', 'Storage Unit',
            'Shelf', 'Rack', 'Box', 'Unit Type'
        ])

        for s in export_samples:
            writer.writerow(s)
        return response

    elif action == 'export_excel' or action == 'export_excel_for_backup':
        file_path = os.path.join(settings.MEDIA_ROOT, 'files/excel_import_template.xlsx')
        workbook = load_workbook(file_path)
        worksheet = workbook['Strain Data']

        for s in export_samples:
            worksheet.append(s)
        
        workbook.active = workbook['Strain Data']
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{timestamp}.samples_backup.xlsx"'
        
        if action == 'export_excel_for_backup':
            backup_file_name = f'{timestamp}.samples_backup.xlsx'
            backup_file_path = os.path.join(settings.MEDIA_ROOT, 'backup_files', backup_file_name)
            workbook.save(backup_file_path)
            return backup_file_path
        else:
            workbook.save(response)
            return response    

def save_storage_data_to_session(request, storage_instance):
    for field in storage_instance._meta.get_fields():
        value = getattr(storage_instance, field.name)
        if field.auto_created and not field.concrete:
            continue
        if isinstance(field, ForeignKey):
            if value:
                request.session[field.name] = value.pk
            else:
                request.session[field.name] = None
        else:
            request.session[field.name] = value
    request.session.save()

def sample_detail(request, pk):
    request.session['sample_list'] = [pk]
    sample = get_object_or_404(Sample, pk=pk)
    if sample.storage_id:
        save_storage_data_to_session(request, sample.storage_id)
    column_mapping = {
        "ID": sample.id,
        "Lab NB Page Number": sample.labnb_pgno,
        "Label Note": sample.label_note,
        "Organism Type": sample.organism_type,
        "Material Type": sample.material_type,
        "Host Species": sample.species,
        "Host Strain": sample.host_strain,
        "Host ID": sample.host_id,
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
        "Tag": sample.tag,
        "Contamination Status": sample.status_contamination,
        "QC Status": sample.status_QC,
        "Physical Status": sample.status_physical,
        "Shared With": sample.shared_with,
        "Is Protected": sample.is_protected,
        "Sequencing Infos": sample.sequencing_infos,
        "Plasmids": sample.plasmids,
        "Antibiotics": sample.antibiotics,
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
            "Box": storage.box,
            "Unit Type": storage.unit_type,
        }
    return render(request, 'KauffmanLabApp/sample_detail.html', {'sample': sample, 'column_mapping': column_mapping, 'storage_mapping': storage_mapping,})


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

def upload_excel(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                messages.success(request, "File Uploaded Successfully")
                excel_file = request.FILES['excel_file']
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(excel_file.read())
                temp_file.close()
                request.session['excel_file_path'] = temp_file.name
                request.session['excel_file_name'] = excel_file.name
                existing_samples, new_samples = check_existing_new_samples(request, excel_file)
                if existing_samples or new_samples:
                    existing_samples_list = ''.join(f'<li>{sample}</li>' for sample in existing_samples)
                    new_samples_list = ''.join(f'<li>{sample}</li>' for sample in new_samples)
                    confirm_message = (
                        f"Are you sure you want to import data from {excel_file.name}?\n"
                        f"<br/> Actions:"
                        f"<ul>"
                        f"  <li>Update Samples:<ul>{existing_samples_list}</ul></li>"
                        f"  <li>Add Samples:<ul>{new_samples_list}</ul></li>"
                        f"</ul>"
                    )
                    form = ConfirmationForm(request.POST, confirm_message=confirm_message)
                    return render(request, 'KauffmanLabApp/confirmation_page.html', {'form': form})
                else:
                    return redirect('sample_list')
            else:
                for _, error in form.errors.items():
                    messages.error(request, error.as_text())
        else:
            form = ConfirmationForm(request.POST)
            if form.is_valid() and form.cleaned_data['confirm']:
                # Retrieve the file from session
                excel_file_path = request.session.get('excel_file_path')
                excel_file_name = request.session.get('excel_file_name')
                with open(excel_file_path, 'rb') as f:
                        excel_file_content = ContentFile(f.read(), name=excel_file_name)
                try:
                    # Process the uploaded Excel file
                    process_excel_file(request, excel_file_content)
                except Exception as e:
                    messages.error(request, str(e))
                finally:
                    os.remove(excel_file_path)
                return redirect('sample_list')
            else:
                messages.info(request, "File upload cancelled.")
                return redirect('sample_list')
    else:
        form = ExcelUploadForm()
    return render(request, 'KauffmanLabApp/upload_excel.html', {'form': form})

def replace_nan_with_blank(data):
    return {k: ('' if pd.isna(v) else v) for k, v in data.items()}

def convert_yes_no_to_boolean(value):
    if isinstance(value, str):
        if value.lower() == 'yes':
            return True
        elif value.lower() == 'no':
            return False
    return value

def check_existing_new_samples(request, excel_file):
    sheet_name = 'Strain Data'
    existing_samples = []
    new_samples = []
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
    except:
        messages.error(request, "Incorrect excel file template")
        return existing_samples, new_samples
    ids = df['ID'].tolist()

    # Iterate over rows and import data into the database
    for sample_id in ids:
        # Check if the sample already exists
        try:
            sample = Sample.objects.get(id=sample_id)
            existing_samples.append(sample_id)
        except Sample.DoesNotExist:
            new_samples.append(sample_id)

    return existing_samples, new_samples

def process_excel_file(request, excel_file):
    # Define mapping of Excel column names to Django model field names
    excel_to_django_field_map = {
    'ID': 'id',
    'Lab NB Page No': 'labnb_pgno',
    'Label Note': 'label_note',
    'Organism Type': 'organism_type',
    'Material Type': 'material_type',
    'Host Species': 'host_species',
    'Host Strain': 'host_strain',
    'Host ID': 'host_id',
    'Storage Solution': 'storage_solution',
    'Lab Lot No': 'lab_lotno',
    'Owner': 'owner',
    'Benchling Link': 'benchling_link',
    'Is Sequenced': 'is_sequenced',
    'Parent Name': 'parent_name',
    'General Comments': 'general_comments',
    'Genetic Modifications': 'genetic_modifications',
    'Species': 'species',
    'Strain Name Main': 'strainname_main',
    'Strain Name Core': 'strainname_core',
    'Strain Name Other': 'strainname_other',
    'Strain Name ATCC': 'strainname_atcc',
    'ATCC Link': 'strain_link',
    'Source Name': 'source_name',
    'Is Purchased': 'is_purchased',
    'Source Lot No': 'source_lotno',
    'Is Under MTA': 'is_undermta',
    'Source Recommended Media': 'source_recommendedmedia',
    'Tag': 'tag',
    'Contamination Status': 'status_contamination',
    'QC Status': 'status_QC',
    'Physical Status': 'status_physical',
    'Shared With': 'shared_with',
    'Is Protected': 'is_protected',
    'Sequencing Infos': 'sequencing_infos',
    'Plasmids': 'plasmids',
    'Antibiotics': 'antibiotics',
    'University Name': 'storage_id.university_name',
    'Room Number': 'storage_id.room_number',
    'Storage Unit': 'storage_id.storage_unit',
    'Shelf': 'storage_id.shelf',
    'Rack': 'storage_id.rack',
    'Box': 'storage_id.box',
    'Unit Type': 'storage_id.unit_type',
    }

    # Read Excel file into a DataFrame
    sheet_name = 'Strain Data'
    df = pd.read_excel(excel_file, sheet_name=sheet_name if sheet_name else 'Sheet1')


    # Iterate over rows and import data into the database
    for index, row in df.iterrows():
        sample_data = {}
        storage_data = {}
        
        for excel_column, model_field in excel_to_django_field_map.items():
            value = row[excel_column]
            value = convert_yes_no_to_boolean(value)

            if model_field.startswith('storage_id.'):
                storage_field = model_field.split('.', 1)[1]
                storage_data[storage_field] = value
            else:
                sample_data[model_field] = value
        
        # Replace NaN values with blank strings
        sample_data = replace_nan_with_blank(sample_data)
        storage_data = replace_nan_with_blank(storage_data)

        # Create or get related Storage object
        if storage_data['university_name'] is not None and storage_data['room_number'] is not None and storage_data['storage_unit'] is not None:
            try:
                # Lookup for University
                university_name = storage_data.pop('university_name').strip()
                university = University.objects.get(university_name__iexact=university_name)

                # Lookup for Room
                room_number = storage_data.pop('room_number')
                room = Room.objects.get(room_number=room_number, university_name=university)
                
                # Lookup for StorageUnit
                storage_unit_value = storage_data.pop('storage_unit').strip()
                storage_unit = StorageUnit.objects.get(storage_unit__iexact=storage_unit_value, room_number=room)
                
                # Lookup for Shelf
                shelf_value = storage_data.pop('shelf')
                shelves = Shelf.objects.filter(shelf=shelf_value, storage_unit=storage_unit)
                if shelves.exists():
                    shelf = shelves.first()  # If multiple shelves are found, use the first one
                else:
                    raise Shelf.DoesNotExist(f"No shelf found for value {shelf_value} in storage unit {storage_unit}")
                
                # Lookup for Rack
                rack_value = storage_data.pop('rack').strip()
                racks = Rack.objects.filter(rack__iexact=rack_value, shelf=shelf)
                if racks.exists():
                    rack = racks.first()  # If multiple racks are found, use the first one
                else:
                    raise Rack.DoesNotExist(f"No rack found for value {rack_value} in shelf {shelf}")
                
                # Create or get Storage
                storage = Storage.objects.create(
                    university_name=university,
                    room_number=room,
                    storage_unit=storage_unit,
                    shelf=shelf,
                    rack=rack,
                    **storage_data
                )
                sample_data['storage_id'] = storage
            
            except (University.DoesNotExist, Room.DoesNotExist, StorageUnit.DoesNotExist, Shelf.DoesNotExist, Rack.DoesNotExist) as e:
                # Handle the case where any of the objects do not exist
                messages.warning(request, f"One or more related objects do not exist: {e}")
        else:
            messages.warning(request, "Skipping processing due to empty values in storage_data.")

        # Handle foreign keys for OrganismType and UserProfile
        sample_data = handle_foreign_data(sample_data, 'organism_type', OrganismType, field='organism_type')
        sample_data = handle_foreign_data(sample_data, 'owner', UserProfile, field='first_last_name')
        sample_data = handle_foreign_data(sample_data, 'status_physical', PhysicalStatus, field='name')
        
        # Create or update Sample object
        sample_id = sample_data.pop('id')  # Assuming ID is a required field
        sample, created = Sample.objects.update_or_create(id=sample_id, defaults=sample_data)
    messages.success(request, 'Import completed successfully.')

def download_excel_template(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'files/excel_import_template.xlsx')

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, filename='template.xlsx')
    else:
        return HttpResponse("File not found.", status=404)

@user_passes_test(lambda u: u.is_staff)
def form_view(request, form_group):
    print('#### form_group ####', request.method, form_group)
    form_group_mapping = {
        'sample_insert_single': {
            'key': 'id',
            'next': 'sample_form'
        },
        'sample_insert_bulk': {
            'keys': ['start_id', 'end_id'],
            'next': 'sample_form'
        },
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
        'storage_unit_type': { #this is just for getting 'box', 'unit_type' from session
            'keys' : ['box', 'unit_type']
        }
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
                if next_form_group:
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
                    clear_session_data(request)
                    request.session['sample_list'] = [id]
                    request.session.save()
                    messages.success(request, f'Sample {id} inserted successfuly')
                elif 'start_id' and 'end_id' in request.session:
                    start_id = request.session.get('start_id', None)
                    end_id = request.session.get('end_id', None)
                    data['start_id'] = start_id
                    data['end_id'] = end_id
                    save_sample(data, 'bulk')
                    clear_session_data(request)
                    sample_list =  get_bulk_sample_ids(start_id, end_id)
                    request.session['sample_list'] = sample_list
                    request.session.save()
                    messages.success(request, f'Samples {start_id} to {end_id} inserted successfuly')        
                
                return redirect('form_view', form_group='storage_samples')
                # return redirect('sample_list')
            
            elif form_group=='storage_unit_type':
                box = form.cleaned_data.get('box')
                unit_type = form.cleaned_data.get('unit_type')
                request.session['box'] = box
                request.session['unit_type'] = unit_type
                request.session.save()
                save_storage(request)
                return redirect('sample_list')
    else:
        filter_kwargs = None
        initial_values = {}
        if form_group in form_group_mapping:
            mapping = form_group_mapping[form_group]
            keys = mapping.get('keys', [])
            if keys:
                for key in keys:
                    if key in request.session:
                        initial_values[key] = request.session[key]
            else:
                key = mapping['key']
                if key in request.session:
                    initial_values[key] = request.session[key]
        if form_group.startswith('storage_'):
            # Retrieve filter data from session for storage forms
            filter_kwargs = set_filtered_dropdown(request, form_group)
        form = DynamicForm(form_group=form_group, filter_kwargs = filter_kwargs, initial_values=initial_values)  

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

    data = handle_foreign_data(data, 'organism_type', OrganismType)
    data = handle_foreign_data(data, 'owner', UserProfile, field='auth_user__username')
    data = handle_foreign_data(data, 'status_physical', PhysicalStatus)
    
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

def get_storage_data_from_session(request):
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
    return storage_data

def save_storage(request):
    # Retrieve sample list and storage data from session
    print("=== save_storage ===")
    sample_list = request.session.get('sample_list', [])
    storage_data = get_storage_data_from_session(request)
    updated_samples = []
    added_samples = []
    
    try:
        with transaction.atomic():
            for sample_id in sample_list:
                sample, created = Sample.objects.get_or_create(id=sample_id)
                
                if sample.storage_id:
                    storage_data['sample'] = sample
                    storage_data['id'] = sample.storage_id.id
                    storage = Storage.objects.get(id=sample.storage_id.id)
                    for key, value in storage_data.items():
                        setattr(storage, key, value)
                    storage.save()
                    updated_samples.append(sample_id)
                else:
                    storage = Storage.objects.create(**storage_data)
                    storage.save()
                    sample.storage_id = storage
                    sample.save()
                    added_samples.append(sample_id)
                
        # Prepare success messages
        if added_samples:
            added_samples_str = ', '.join(map(str, added_samples))
            messages.success(request, f'Success: ADDED storage info for {added_samples_str}')

        if updated_samples:
            updated_samples_str = ', '.join(map(str, updated_samples))
            messages.success(request, f'Success: UPDATED storage info for {updated_samples_str}')
    
    except Exception as e:
        messages.error(request, f'Error saving storage info: {e}')

def add_bulk_storage(request, selections):
    request.session['sample_list'] = selections
    return redirect('form_view', form_group='storage_samples')

def get_bulk_sample_ids(start_id, end_id):
    start = int(start_id[-3:])
    end = int(end_id[-3:])
    prefix = end_id[:-3]
    sample_ids = [f"{prefix}{i:03d}" for i in range(start, end + 1)]
    return sample_ids

def backup_and_upload(request):
    # script_path = os.path.join(os.getcwd(), 'KauffmanLabApp', 'backup_database.py')
    script_path = "/Users/jatinchhabria/Documents/KauffmanLabProject/KauffmanLabApp/backup_database.py"
    try:
        result = subprocess.run(
            ['python', script_path], capture_output=True, text=True, check=True
        )
        if result.returncode == 0:
            messages.success(request, "Backup successful")
        else:
            messages.error(request, "Backup failed")
    except subprocess.CalledProcessError as e:
        print(f'Backup script error: {e.stderr}')
        messages.error(request, f"Backup failed: {e.stderr}")
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        messages.error(request, f"Unexpected error occurred: {str(e)}")

    return redirect('admin_panel')

