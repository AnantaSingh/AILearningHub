# Generated by Django 4.2.10 on 2025-03-01 20:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookmarks', '0004_alter_bookmark_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together={('user', 'url')},
        ),
        migrations.AddField(
            model_name='bookmark',
            name='is_bookmarked',
            field=models.BooleanField(default=True),
        ),
        migrations.RemoveField(
            model_name='bookmark',
            name='bookmark_user',
        ),
    ]
