# Generated by Django 2.1.1 on 2019-01-20 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradeuser',
            name='grade',
            field=models.CharField(max_length=20, null=True, verbose_name='Grade'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='grade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.GradeUser'),
        ),
    ]
