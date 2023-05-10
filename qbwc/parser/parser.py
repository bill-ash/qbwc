import xml.etree.ElementTree as ET


def string_to_xml(s):
    return ET.fromstring(s)


def parse_query_element(element, prefix=""):
    data = {}
    for child in element:
        if len(child) > 0:
            data = {**parse_query_element(child, child.tag), **data}
        else:
            data[f"{prefix}{child.tag}"] = child.text
    return data
