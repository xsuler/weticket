# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-10-16 15:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityimage',
            name='image',
            field=models.ImageField(default='static/activity_image/None/no-img.jpg', upload_to='activity_image/'),
        ),
    ]