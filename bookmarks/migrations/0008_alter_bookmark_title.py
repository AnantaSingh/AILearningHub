# Generated by Django 5.1.6 on 2025-03-04 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookmarks", "0007_alter_bookmark_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookmark",
            name="title",
            field=models.CharField(max_length=255),
        ),
    ]
