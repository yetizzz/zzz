"""
Basic API client

To populate some data::

    python client.py create

To query that data::

    python client.py list

To search that data::

    python client.py list <slug__startswith>

To delete all the data::

    python client.py delete

"""

import json
import sys

import slumber

api = slumber.API("http://localhost:8000/api/v1/")
LIMIT = 500
test_data = [
    ["rtd", "http://readthedocs.org"],
    ["google", "http://google.com"],
    ["google", "http://google.com/2/"],
    ["dash", "http://djangodash.com"],
]


if len(sys.argv) > 1:
    if sys.argv[1] == 'create':
        for data in test_data:
            key, url = data

            try:
                resp = api.hydra.post({"slug": key, "urls": [url]})
                print "WOOT"
                print resp
            except Exception, e:
                print e
                try:
                    ret = json.loads(e.content)
                    print ret['traceback']
                except:
                    pass
    if sys.argv[1] == 'list':
        if len(sys.argv) == 3:
            ret = api.hydra.get(slug=sys.argv[2], limit=LIMIT)
        else:
            ret = api.hydra.get(limit=LIMIT)
        for ret in ret['objects']:
            print ret['slug']

    if sys.argv[1] == 'delete':
        ret = api.hydra.get(limit=LIMIT)
        for ret in ret['objects']:
            slug = ret['slug']
            print slug,
            print " - Deleted: %s" % api.hydra(slug).delete()
