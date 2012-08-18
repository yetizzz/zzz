import operator

from sphinx.ext import intersphinx

from hydra.api import r, save, make_slug, get_keys

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
