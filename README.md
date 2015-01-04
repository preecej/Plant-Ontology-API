# Araport Community API v0.3 Tutorial

## Tutorial 1: Creating a 'generic' service to access the MapMan bins API

Behind the scenes of our API, we need to issue an HTTP request modelled after the following:

```
GET http://www.gabipd.org/services/rest/mapman/bin?request=[{"agi":"At4g25530"}]
```

We expect a JSON response resembling this one:

```JSON
[
    {"request":
        {"agi":"At4g25530"},
     "result":[
        {"code":"27.3.22",
         "name":"RNA.regulation of transcription.HB,Homeobox transcription factor family",
         "description":"no description",
         "parent":
            {"code":"27.3",
             "name":"RNA.regulation of transcription",
             "description":"no description",
             "parent":
                {"code":"27",
                 "name":"RNA",
                 "description":"no description",
                 "parent":null}}}]}]
```

This JSON response, while not conforming to the emergent AIP data schema, is perfectly valid JSON. So, we will go ahead and return it to consumers. However, we will normalize the input parameters to use the AIP "locus" parameter name instead of accepting a JSON object. We will implement a "generic" type API to accomplish these objectives. 

### Editing and testing some code

Open up `workshop_tutorial_api/generic_demo/main.py` in your text editor. You will see that the stubbed in `search()` function has been replaced with a lot more text, which has all been commented out. We will gradually remove comments, testing along the way, to demonstrate key concepts in building a generic Data API for Araport.

```python
# arg contains a dict with a single key:value
# locus is AGI identifier and is mandatory
    
    # Return nothing if client didn't pass in a locus parameter
    # if not ('locus' in arg):
    #    return
    
    # Validate against a regular expression
    # locus = arg['locus']
    # locus = locus.upper()
    # p = re.compile('AT[1-5MC]G[0-9]{5,5}', re.IGNORECASE)
    # if not p.search(locus):
    #    return

    # param = '[{%22agi%22:%22' + locus + '%22}]'
    # r = requests.get('http://www.gabipd.org/services/rest/mapman/bin?request=' + param)
    
    # print r.headers['Content-Type']
    # print r.text
    
    # if r.ok:
    #    return r.headers['Content-Type'], r.content
    # else:
    #   return 'text/plaintext; charset=UTF-8', 'An error occurred on the remote server'
```

#### Parameter validation

Let's implement handling of the 'locus' parameter. The ADAMA service that powers our community APIs will eventually take on validation of parameters but for now, if you want robust web services you need to add in some error handling. 

Uncomment the following code blocks:

```python
    # Return nothing if client didn't pass in a locus parameter
     if not ('locus' in arg):
        return
    
    # Validate against a regular expression
     locus = arg['locus']
     locus = locus.upper()
     p = re.compile('AT[1-5MC]G[0-9]{5,5}', re.IGNORECASE)
     if not p.search(locus):
        return
```

Now, let's go test it out in a Python environment. Remember that you should be in a virtual environment with the `requests` module available because we imported it at the start of `main.py`. 

```
Python 2.7.6 (default, Sep  9 2014, 15:04:36) 
[GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.39)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import main
>>> main.search({'locus':'AT4G25530'})
AT4G25530
>>> main.search()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: search() takes exactly 1 argument (0 given)
>>> main.search({'foo':'AT4G25530'})
>>> main.search({'locus':'bar'})
>>>
```

Notable observations:
1. We invoke the main's search method with a python dict. This emulates the way the ADAMA master server sends parameters to your code
2. Our code validation first checks for the existence of the locus key and returns if not present
3. The code validation next checks for a valid locus name via regex and returns if not found
4. If we fail to pass in a dict to `search()`, there is also a failure response

#### Using Python requests

We're ready to wire up an HTTP GET request to the MapMan web service. A simple form of the Python `requests` module is demonstrated here - if you're not familiar with it you may want to [check out its documentation in detail](http://docs.python-requests.org/en/latest/).

Uncomment the following code blocks:

```python
    # Construct an access URL for the MapMan API
    param = '[{%22agi%22:%22' + locus + '%22}]'
    r = requests.get('http://www.gabipd.org/services/rest/mapman/bin?request=' + param)
    
    # Debug: Print the headers and text response
    print r.headers['Content-Type']
    print r.text
```

Test out the code in your Python environment. If you have the previous Python interpreter still active, type `reload(main)` instead of import main below.


```python
>>> import main
>>> main.search({'locus':'AT4G25530'})
application/json
[{"request":{"agi":"AT4G25530"},"result":[{"code":"27.3.22","name":"RNA.regulation of transcription.HB,Homeobox transcription factor family","description":"no description","parent":{"code":"27.3","name":"RNA.regulation of transcription","description":"no description","parent":{"code":"27","name":"RNA","description":"no description","parent":null}}}]}]
```

#### Returning a response

We're now ready to return the response to the client. In a generic Araport API, we accomplish this by returning two obejcts: a valid content-type and the content of the remote server's HTTP response. You can also generate your own data to transmit to the client (for instance, GFF records or comma-separated value rows). 

Re-comment and uncomment the following code blocks

```python
    #print r.headers['Content-Type']
    #print r.text
    
    if r.ok:
        return r.headers['Content-Type'], r.content
    else:
        return 'text/plaintext; charset=UTF-8', 'An error occurred on the remote server'
```        

Technically, for this use case we could just return the header provided by the remote service and its content, but we are being clever and checking for 200 OK. We return a plaintext error if we don't see see a server code of 200 in the response from the MapMan remote API. 

We can test out the service locally in your Python interpreter now (an exercise left to the reader). When we are sure it's working, it's time to register the service under the Araport `/community` API. 

#### A quick trip through metadata.yml

Every Araport service is described using a metadata file written in [YAML format](http://www.yaml.org/). Our service's metadata file is pasted in below:

```YAML
---
description: "Returns MapMan bin information for a given AGI locus identifier using the generic type of Araport web service"
main_module: generic_demo/main.py
name: generic_mapman_bin_by_locus
type: generic
url: "http://www.gabipd.org/"
version: 0.1
whitelist:
  - www.gabipd.org
```

* name is a lexically unique, lowercase-only identifier for the service
* version is the version of the Araport service
* description is a human-readable description
* main_module defines where, relative to the root of the Git repo, we find the main file for the service
* type is one of the supported Araport service types
* url is optional in this case, but points to the top level URL of the service
* whitelist is a set of addresses that our service can communicate with. If you forget to specify this, your service will fail to work

#### Registering your service with Araport

If you want to save your current work, please do the following in your `local workshop_tutorial_api` directory

```bash
git add .
git commit -m "In progress!"
```

Checkout the next branch to migrate to a fully functional code repo that we can be sure will work as a web services. Follow along with the instructions in the README.md file under that branch.

```bash
git checkout "tutorial/2"
```
