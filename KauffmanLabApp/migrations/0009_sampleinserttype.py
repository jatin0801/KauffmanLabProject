# Generated by Django 4.2.10 on 2024-06-03 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KauffmanLabApp', '0008_alter_variablelabelmapping_choice_id_field_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampleInsertType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('insert_type', models.CharField(max_length=255)),
            ],
        ),
    ]
