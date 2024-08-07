# Generated by Django 4.2.10 on 2024-06-15 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('KauffmanLabApp', '0011_variablelabelmapping_help_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='storage_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='KauffmanLabApp.storage'),
        ),
        migrations.AlterField(
            model_name='variablelabelmapping',
            name='field_type',
            field=models.CharField(choices=[('char', 'CharField'), ('select', 'SelectField'), ('boolean', 'BooleanField'), ('integer', 'IntegerField'), ('email', 'EmailField'), ('file', 'FileField'), ('url', 'URLField'), ('typedchoice', 'TypedChoiceField'), ('multiplechoice', 'MultipleChoiceField'), ('typedmultiplechoice', 'TypedMultipleChoiceField'), ('select2tag', 'Select2TagField')], max_length=25),
        ),
    ]
