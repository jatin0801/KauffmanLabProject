# Generated by Django 4.2.10 on 2024-09-22 16:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('KauffmanLabApp', '0019_remove_sample_is_discarded_remove_sample_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='antibiotics',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='sample',
            name='plasmids',
            field=models.TextField(blank=True, null=True),
        ),
    ]
