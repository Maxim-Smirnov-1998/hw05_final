# Generated by Django 2.2.16 on 2022-04-02 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20220402_1112'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='create',
            new_name='created',
        ),
    ]
