# Generated by Django 4.2.10 on 2025-03-01 00:59

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resource',
            options={'verbose_name_plural': 'Resources'},
        ),
        migrations.AddField(
            model_name='resource',
            name='difficulty_level',
            field=models.CharField(choices=[('BEGINNER', 'Beginner'), ('INTERMEDIATE', 'Intermediate'), ('ADVANCED', 'Advanced')], default='INTERMEDIATE', max_length=20),
        ),
        migrations.AddField(
            model_name='resource',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name='resource',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='tags',
            field=models.CharField(blank=True, help_text='Comma-separated tags', max_length=500),
        ),
        migrations.AddField(
            model_name='resource',
            name='votes_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddIndex(
            model_name='resource',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='resources_r_search__82e125_gin'),
        ),
    ]
