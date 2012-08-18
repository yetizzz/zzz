import os
from django.core.management.base import NoArgsCommand
from django.conf import settings

from hydra.utils import read_intersphinx

INV_MAPPING = {
    'rtd.inv': 'http://read-the-docs.readthedocs.org/en/latest/%s',
    'django.inv': 'http://django.readthedocs.org/en/latest/%s',
}

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        for proj, url in INV_MAPPING.iteritems():
            read_intersphinx(os.path.join(settings.ROOT_DIR, proj), url)


