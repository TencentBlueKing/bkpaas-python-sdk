# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand
from paas_service.tasks import clean_instances

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Aim to clean all instances which should be cleaned"

    def handle(self, *args, **options):
        print("start to clean instances")
        clean_instances()
        print("cleaned. ")
