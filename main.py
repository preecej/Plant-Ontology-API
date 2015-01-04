import requests
import re
import json

def search(arg):
    
# arg contains a dict with a single key:value
# term is PO accession term and is mandatory
    
    # Return nothing if client didn't pass in a term parameter
    if not ('term' in arg):
       return
    
    # Validate against a regular expression
    term = arg['term']
    #term = term.upper()
    p = re.compile('[A-Z,a-z,0-9]', re.IGNORECASE)
    if not p.search(term):
       return

    r = requests.get('http://palea.cgrb.oregonstate.edu/services/PO_web_service.php?request_type=term_search&search_value=' + term + '&inc_synonyms&branch_filter=plant_anatomy&max=20&prioritize_exact_match')
    
    #print r.headers['Content-Type']
    #print r.text
    
    if r.ok:
       return r.headers['Content-Type'], r.content
    else:
      return 'text/plaintext; charset=UTF-8', 'An error occurred on the remote server'

def list(arg):
    pass
