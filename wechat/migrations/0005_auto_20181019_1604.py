# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-10-19 16:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0004_auto_20181019_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
