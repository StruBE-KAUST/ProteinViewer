# -*- coding : utf-8 -*-

##    Copyright (C) 2017 King Abdullah University of Science and Technology
##
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License along
##    with this program; if not, write to the Free Software Foundation, Inc.,
##    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Remove old session files. Delay is set in config file."""

import logging
import os
import shutil
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps

from ProteinViewer.models import ViewingSession


class Command(BaseCommand):
    """Remove viewing_session temporary directories older than settings.delay."""

    help = 'Remove static folders for viewing sessions older than '\
        'config.ini -> keep_time (in days).'

    def handle(self, *args, **options):
        """Remove old static directories."""
        log = logging.getLogger(__name__)
        log.debug("Enter")

        # Get delay
        delay = apps.get_app_config('ProteinViewer').session_delay
        min_date = datetime.today() - timedelta(days = delay + 2)
        max_date = datetime.today() - timedelta(days = delay)

        to_clean = ViewingSession.objects.filter(
            date_created__range=[min_date, max_date])

        for session in to_clean:
            to_rm_dir = os.path.join(settings.MEDIA_ROOT,
                    session.temporary_directory)
            log.info("Remove directory: " + str(to_rm_dir))
            shutil.rmtree(to_rm_dir)

        log.debug("Exit")
