
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import phonenumbers

osm_file = open("sampleAustin.osm", "rb")

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)
post_codes = defaultdict(int)
phones = defaultdict(int)
attributes = set()


mapping = { "St": "Street",
            "St.": "Street",
            'Blvd' : "Boulevard",
            "Rd" : "Road",
            "rd" : "Road", 
            "Ct" : "Court",
            "ct" : "Court",
            "Cv" : "Cove",
            "Dr" : "Drive", 
            "dr" : "Drive", 
            "Cir" : "Circle", 
            "cir" : "Circle",
            "Dr." : "Drive",
            "Ct." : "Court"


            }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()

        street_types[street_type] += 1
# look at zip codes 

def audit_post_code(post_codes, post_code):
    p = post_code
    if p: 
        post_code = p
        post_codes[post_code] += 1

#look at phone numbers 

def audit_phone(phones, phone): 
    ph = phone
    if ph: 
        phone = ph
        phones[phone] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print('{}: {}'.format(k, v))


#audit street type "addr:street"
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

#audit zip codes "addr:postcode"
def is_post_code(elem): 
    return(elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode")

#audit city: "addr:city"
def is_city(elem):
    return(elem.tag == "tag") and (elem.attrib['k'] == "addr:city")


def is_phone(elem):
    return(elem.tag == "tag") and ((elem.attrib['k'] == "phone") or (elem.attrib['k'] == "contact:phone"))


def audit():  #Initial audit function to validate data cleanliness actions
    for event, elem in ET.iterparse(osm_file):
        if is_phone(elem): 
           # audit_phone(phones, elem.attrib['v'])
           print(clean_phone(elem.attrib['v']))
        if is_post_code(elem):
            print(fix_postcode(elem.attrib['v']))
        if is_street_name(elem):
            print(update_name(elem.attrib['v'], mapping))
    osm_file.close()
          

    


def update_name(name, mapping):  #k value of addr:street, mapping to street inaccuracies & accuracies
    for key, value in mapping.items(): 
        if key == name:
            return name.replace(key, value)
    return(name)

def clean_phone(phone):  #v value of k "phone"
    try: 
        cleaned_ph = phonenumbers.format_number(phonenumbers.parse(phone, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        return(cleaned_ph)
    except:
        pass

def fix_postcode(postcode): #v value of k addr:postcode
    fixed_zip = postcode[:5]
    return(fixed_zip)

if __name__ == '__main__':
    audit()
