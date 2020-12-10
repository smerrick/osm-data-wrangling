
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

filenames = ['./austinmap.osm', './nodes_tags.csv', './nodes.csv', './ways_nodes.csv', './ways_tags.csv', './ways.csv']

for item in filenames: 
    print(item, ' size: ', (os.stat(item).st_size)/1000, ' MB')