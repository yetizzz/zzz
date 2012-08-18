import os
import operator
import requests

from sphinx.ext import intersphinx
from django.core.management.base import NoArgsCommand
from django.conf import settings

from hydra.api import r, save, make_slug


def safe_save(slug, url):
    if not r.keys(make_slug(slug)):
        save(slug, url)


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        read(os.path.join(settings.ROOT_DIR, 'django.inv'))


def read(file):
    urlpattern = 'http://django.readthedocs.org/en/latest/%s'
    f = open(file)
    #wtf?
    f.readline()
    data = intersphinx.read_inventory_v2(f, urlpattern, operator.mod)
    for top_key in data.keys():
        print "KEY: %s" % top_key
        inner_keys = data[top_key].keys()
        for inner_key in inner_keys:
            #print "INNER KEY: %s" % inner_key
            project, version, url, title = data[top_key][inner_key]
            url_key = url.split('#')[1]
            if ":" in url_key:
                #This dumps junk data into the url namespace we don't need
                print "INNER: %s->%s" % (inner_key, url)
                safe_save(inner_key, url)
            else:
                last_key = url_key.split('.')[-1]
                if last_key != url_key:
                    #Only save last key if it differes
                    print "LAST: %s->%s" % (last_key, url)
                    #save(last_key, url)
                print "URL: %s->%s" % (url_key, url)
                safe_save(url_key, url)
