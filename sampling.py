import xml.etree.ElementTree as ET

OSM_FILE = "rj_map.osm"
SAMPLE_FILE = "sample_rj_map.osm"

k = 100

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """
        Parses through file and gets specified elements.
        Args: 
            osm_file: OpenStreetMap data
            tags: The three tags of interest; node, way, and relation.
        Yield:
            Yield element if it is the right type of tag
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

with open(SAMPLE_FILE, 'wb') as output:
    """ Creates a subset of the code for every kth element """
    #output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    #output.write('<osm>\n  ')

    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    #output.write('</osm>')
