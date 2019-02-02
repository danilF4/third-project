# Generated by Django 2.1.1 on 2019-01-20 22:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0008_auto_20190120_1649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='viewed',
        ),
        migrations.AddField(
            model_name='post',
            name='viewed',
            field=models.ManyToManyField(blank=True, related_name='post_viewed', to=settings.AUTH_USER_MODEL),
        ),
    ]
