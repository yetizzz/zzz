import slumber
import json

api = slumber.API("http://localhost:8000/api/v1/")

test_data = [
    ["rtd", "http://readthedocs.org"],
    ["google", "http://google.com"],
    ["dash", "http://djangodash.com"],
]

for data in test_data:
    key, url = data

    try:
        resp = api.hydra.post({"key": key, "url": url})
        print "WOOT"
        print resp
    except Exception, e:
        try:
            ret = json.loads(e.content)
            print ret['traceback']
        except:
            pass
