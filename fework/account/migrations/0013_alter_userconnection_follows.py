# Generated by Django 4.2.5 on 2023-12-05 10:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_remove_workappreciation_likes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userconnection',
            name='follows',
            field=models.ManyToManyField(blank=True, related_name='followed_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
