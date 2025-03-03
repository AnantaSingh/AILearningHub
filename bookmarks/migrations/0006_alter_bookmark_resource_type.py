# Generated by Django 4.2.10 on 2025-03-04 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookmarks", "0005_alter_bookmark_unique_together_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bookmark",
            name="resource_type",
            field=models.CharField(
                choices=[
                    ("GITHUB", "GitHub Repository"),
                    ("PAPER", "Research Paper"),
                    ("COURSE", "Online Course"),
                    ("BLOG", "Blog Post"),
                    ("COMMUNITY", "Community Resource"),
                    ("DOCUMENTATION", "Documentation"),
                    ("BOOK", "Book"),
                ],
                max_length=20,
            ),
        ),
    ]
