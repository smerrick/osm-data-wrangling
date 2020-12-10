# Wrangling Open Street Map Data
## Siobhan Merrick

**Map Area:**

[Austin, TX, USA](https://www.openstreetmap.org/relation/113314)

I've lived in Austin for > 25 years, so I'm very familiar with the area. 

## Problems Encountered in the Dataset

After creating a sample of the document to perform some exploration using every 20th record as the sample, leveraging the code snippets provided in the course documentation,  I decided on a couple of things. 

I began to audit the data for inconsistencies. Creating new functions for types of audit were helpful, and some results that required cleanup included: 

1. Street types.  While mostly clean, there were some instances where abbreviations affected the totality of some names that could be cleaned, primarily abbreviations for Cove, Lane, Street, and Boulevard. 

```python
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit():
    for event, elem in ET.iterparse(osm_file):
        if is_street_name(elem):
            audit_street_type(street_types, elem.attrib['v'])    
    print_sorted_dict(street_types)    
```
To update these, I created a function in Audit.py to update these values based on a mapping created of sample data discrepancies: 

```python
def update_name(name, mapping):
    for key, value in mapping.iteritems(): 
        if key == name:
            return name.replace(key, value)
    return(name)

```

2. In validating postal codes, the data was mainly clean except for one zip that had the following 4 digits.  Those will need to have the length trimmed.  I might also perform a check to ensure they all start with 7.  A sample of the output: 
```
78721: 36
78722: 17
78723: 102
78724: 96
78724-1199: 1
78725: 51
78726: 19
```
This was a simple approach to fix, where I just retained the first 5 characters in the string.

```python
def fix_postcode(postcode):
    fixed_zip = postcode[:5]
    return(fixed_zip)
```

3.  Phone numbers: When looking at phone numbers, the formats varied widly.  Some included country code (+1), some had the area code in parentheses, some were truncated, and there were various other conditions.  These will need to be normalized.  

```python
def audit_phone(phones, phone): 
    ph = phone
    if ph: 
        phone = ph
        phones[phone] += 1
```

To fix them, I discovered a python library called "phonenumbers" that had formatting logic, so I installed that instead of messing with regex a bunch. (I hate regex)

```python
def clean_phone(phone):
    cleaned_ph = phonenumbers.format_number(phonenumbers.parse(phone, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
    return(cleaned_ph)
```
When generating the csvs, I noticed that there was a tag that showed phone numbers with a different heading: "contact", so I had to go in and adjust the original logic to ensure that "contact:phone" was captured as well. 

4.  There there are numbres of