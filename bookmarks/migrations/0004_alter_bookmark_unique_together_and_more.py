# Generated by Django 4.2.10 on 2025-03-01 20:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookmarks', '0003_bookmark_is_admin_saved'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='bookmark_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookmarked_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together={('bookmark_user', 'url')},
        ),
    ]
