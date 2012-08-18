"""
Basic API client

To populate some data::

    python client.py create

To query that data::

    python client.py get

"""

import json
import sys

import slumber

api = slumber.API("http://localhost:8000/api/v1/")

test_data = [
    ["rtd", "http://readthedocs.org"],
    ["google", "http://google.com"],
    ["dash", "http://djangodash.com"],
]


if len(sys.argv) == 2:
    if sys.argv[1] == 'create':
        for data in test_data:
            key, url = data

            try:
                resp = api.hydra.post({"key": key, "url": url})
                print "WOOT"
                print resp
            except Exception, e:
                print e
                try:
                    ret = json.loads(e.content)
                    print ret['traceback']
                except:
                    pass
    if sys.argv[1] == 'get':
        print api.hydra('awesome').get()
