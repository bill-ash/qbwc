from pathlib import Path 
from qbwc.parser import parse_query_element, string_to_xml

xml_path = Path().absolute()

with open(xml_path / "tests/accounts.xml", "r") as xml:
    qbxml = xml.read()

def test_parser(): 
    root = string_to_xml(qbxml)
    data_list = []
    for account_rs in root.iter("AccountQueryRs"):
        data_list.extend(parse_query_element(q) for q in account_rs.iter("AccountRet"))
        
    assert len(data_list) == 116

