# Generated by Django 3.0.5 on 2020-05-01 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='level',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='uid',
            field=models.CharField(max_length=16, null=True),
        ),
    ]
