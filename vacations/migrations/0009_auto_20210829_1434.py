# Generated by Django 2.2.12 on 2021-08-29 05:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacations', '0008_auto_20210824_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='replaces',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vacations.Employee', verbose_name='Замещает'),
        ),
    ]
