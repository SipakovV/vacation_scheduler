# Generated by Django 2.2.12 on 2021-08-09 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacations', '0003_auto_20210809_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='replaces',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='vacations.Employee', verbose_name='Замещает'),
        ),
    ]
