# Generated by Django 4.1.1 on 2022-09-12 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publishing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.PositiveIntegerField(choices=[(0, 'Published'), (1, 'Draft'), (2, 'Archived'), (3, 'Deleted')], default=0),
        ),
    ]
