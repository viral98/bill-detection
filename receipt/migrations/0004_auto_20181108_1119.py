# Generated by Django 2.0 on 2018-11-08 11:19

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('receipt', '0003_auto_20171112_0052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='date',
            field=models.DateField(default=datetime.datetime(2018, 11, 8, 11, 19, 1, 566677, tzinfo=utc)),
        ),
    ]