import urllib.request
import sys

try:
    resp = urllib.request.urlopen('http://127.0.0.1:5000')
    print('STATUS:', resp.status)
    print('HEADERS:', resp.getheaders())
    print('BODY:', resp.read(200).decode('utf-8', errors='ignore'))
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)
