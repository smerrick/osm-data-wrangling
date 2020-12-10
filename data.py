
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import codecs
import pprint
import re
import xml.etree.ElementTree as ET
from Audit import *
from collections import defaultdict 


OSM_PATH = "austinmap.osm"

NODES_PATH = "nodes.csv"
NODES_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODES_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements


    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in NODE_FIELDS:
                node_attribs[attrib] = element.attrib[attrib]
        for child in element:
            child_tag = {}
            if LOWER_COLON.match(child.attrib['k']):
                child_tag['key'] = child.attrib['k'].split(':',1)[1]
                child_tag['type'] = child.attrib['k'].split(':',1)[0]
                if is_street_name(child):
                    child_tag['value'] = update_name(child.attrib['v'], mapping) #calling Audit.py name clean function
                elif is_post_code(child): 
                    child_tag['value'] = fix_postcode(child.attrib['v']) #calling Audit.py zipcode function
                elif is_phone(child): 
                    child_tag['value'] = clean_phone(child.attrib['v']) #fixes contact:phone k value              
                else:
                    child_tag['id'] = element.attrib['id']
                    child_tag['value'] = child.attrib['v']
                tags.append(child_tag)
            elif PROBLEMCHARS.match(child.attrib['k']):
                continue
            else:    
                child_tag['type'] = default_tag_type
                child_tag['key'] = child.attrib['k']
                child_tag['id'] = element.attrib['id']
                if is_phone(child):
                    child_tag['value'] = clean_phone(child.attrib['v']) #fixes original k value of "phone"
                else:
                    child_tag['value'] = child.attrib['v']
                tags.append(child_tag)

        return {'node': node_attribs, 'nodes_tags': tags}
        
    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]
        
        position = 0
        for child in element:
            wy_tg = {}
            wy_nd = {}
            
            if child.tag == 'tag':
                wy_tg['id'] = element.attrib['id']
                if LOWER_COLON.match(child.attrib['k']):
                    wy_tg['type'] = child.attrib['k'].split(':',1)[0]
                    wy_tg['key'] = child.attrib['k'].split(':',1)[1]
                    if is_street_name(child):
                        wy_tg['value'] = update_name(child.attrib['v'], mapping)
                    elif is_post_code(child): 
                        wy_tg['value'] = fix_postcode(child.attrib['v'])
                    elif is_phone(child): 
                        wy_tg['value'] = clean_phone(child.attrib['v']) 
                    else:
                        wy_tg['value'] = child.attrib['v']
                        tags.append(wy_tg)
                elif PROBLEMCHARS.match(child.attrib['k']):
                    continue
                else:
                    wy_tg['value'] = child.attrib['v']
                    wy_tg['type'] = default_tag_type
                    wy_tg['key'] = child.attrib['k']
                    
                    tags.append(wy_tg)
                    
            elif child.tag == 'nd':
                wy_nd['id'] = element.attrib['id']
                wy_nd['node_id'] = child.attrib['ref']
                wy_nd['position'] = position
                position += 1
                way_nodes.append(wy_nd)

        

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
    

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row): #updated for python 3
        super(UnicodeDictWriter, self).writerow({
            k: v for k, v in row.items()
        })



# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w', 'utf-8') as nodes_file, \
         codecs.open(NODES_TAGS_PATH, 'w', 'utf-8') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w', 'utf-8') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w', 'utf-8') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w', 'utf-8') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        nodes_tags_writer = UnicodeDictWriter(nodes_tags_file, NODES_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        nodes_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    nodes_tags_writer.writerows(el['nodes_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':

    process_map(OSM_PATH, validate=True)
