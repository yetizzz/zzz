import redis
import operator

from django.conf import settings

from sphinx.ext import intersphinx

r = redis.StrictRedis.from_url(settings.REDIS_URL)

def make_slug(val, version="latest"):
    return "hydra:v1:redirects:%s:%s" % (version, val)


def remove_slug(val, version="latest"):
    return val.replace(make_slug('', version=version), "")


def save(slug, url, version="latest"):
    redis_slug = make_slug(slug, version)
    return r.zincrby(redis_slug, url, 1)
    #r.set(redis_slug, urls)


def get_range(pk, withscores=True):
    return r.zrange(make_slug(pk), 0, -1, withscores=withscores)


def get_keys(key):
    return r.keys(make_slug('%s' % key))


def delete(slug):
    return r.delete(make_slug(slug))


def get_urls(slug, count=None):
    ret_val = []
    # Could have defaulted to -1 but that is a less obvious API
    if count is None:
        count = -1
    values = get_range(slug)
    for value in values:
        redirect_url, score = value
        ret_val.append({
            'score': score,
            'url': redirect_url
        })
    return ret_val


def safe_save(slug, url):
    if not get_keys(slug):
        save(slug, url)

def read_intersphinx(file, urlpattern):
    """
    Reads file as intersphinx format. Prepends the url pattern on the front of URLs.
    URL Pattern should have a %s in it for string formatting.
    """
    f = open(file)
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
                    save(last_key, url)
                print "URL: %s->%s" % (url_key, url)
                safe_save(url_key, url)
