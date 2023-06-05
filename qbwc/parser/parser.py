import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def string_to_xml(s):
    return ET.fromstring(s)


def parse_table_elems(s, table):
    elems = list(s.iter(table))
    return [parse_query_element(c) for c in elems]


def truthy(s):
    return s == "true"


def parse_query_element(element, prefix=""):
    data = {}
    for child in element:
        if len(child) > 0:
            data = {**parse_query_element(child, child.tag), **data}
        else:
            data[f"{prefix}{child.tag}"] = child.text
    return data


def check_status(xml):
    return [
        c.attrib.get("statusSeverity")
        for c in xml.iter()
        if "statusSeverity" in c.attrib
    ][0]


def parse_time_stamp(x):
    """Convert stringstamps to datestamps"""
    try:
        return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")
    except Exception:
        logger.error("Error parsing time stamp")
        return datetime.now(timezone.utc)
