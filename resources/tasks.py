from celery import shared_task
from django.core.management import call_command

@shared_task
def update_resources():
    call_command('fetch_resources') 