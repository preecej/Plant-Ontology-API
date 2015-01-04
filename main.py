import requests
import re
import json

def search(arg):
    
# arg contains a dict with a single key:value
# locus is AGI identifier and is mandatory
    
    # Return nothing if client didn't pass in a locus parameter
    if not ('locus' in arg):
       return
    
    # Validate against a regular expression
    locus = arg['locus']
    locus = locus.upper()
    p = re.compile('AT[1-5MC]G[0-9]{5,5}', re.IGNORECASE)
    if not p.search(locus):
       return

    param = '[{%22agi%22:%22' + locus + '%22}]'
    r = requests.get('http://www.gabipd.org/services/rest/mapman/bin?request=' + param)
    
    #print r.headers['Content-Type']
    #print r.text
    
    if r.ok:
       return r.headers['Content-Type'], r.content
    else:
      return 'text/plaintext; charset=UTF-8', 'An error occurred on the remote server'

def list(arg):
    pass
