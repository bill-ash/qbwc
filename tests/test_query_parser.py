from pathlib import Path
from qbwc.parser import parse_query_element, string_to_xml, check_status

xml_path = Path().absolute()

with open(xml_path / "tests/accounts.xml", "r") as xml:
    qbxml = xml.read()


def test_parser():
    root = string_to_xml(qbxml)
    data_list = []
    for account_rs in root.iter("AccountQueryRs"):
        data_list.extend(parse_query_element(q) for q in account_rs.iter("AccountRet"))

    assert len(data_list) == 116


error = """<?xml version="1.0" ?>
            <QBXML>
                <QBXMLMsgsRs>
                <AccountAddRs 
                    statusCode="3070"
                    statusSeverity="Error"
                    statusMessage="The string &quot;a5ad6d73&quot; in the field &quot;AccountNumber&quot; is too long." 
                    />
                </QBXMLMsgsRs>
            </QBXML>
        """

success = """<?xml version="1.0" ?>
        <QBXML>
            <QBXMLMsgsRs>
            <AccountAddRs 
                statusCode="0" 
                statusSeverity="Info" 
                statusMessage="Status OK"
                >
            <AccountRet>
            <ListID>8000009E-1734319187</ListID>
            <TimeCreated>2024-12-15T22:19:47-05:00</TimeCreated>
            <TimeModified>2024-12-15T22:19:47-05:00</TimeModified>
            <EditSequence>1734319187</EditSequence>
            <Name>New Account Name 821f2</Name>
            <FullName>New Account Name 821f2</FullName>
            <IsActive>true</IsActive>
            <Sublevel>0</Sublevel>
            <AccountType>OtherCurrentAsset</AccountType>
            <AccountNumber>eb47de1</AccountNumber>
            <Desc>Hello, World!</Desc>
            <Balance>0.00</Balance>
            <TotalBalance>0.00</TotalBalance>
            <TaxLineInfoRet>
            <TaxLineID>1547</TaxLineID>
            <TaxLineName>B/S-Assets: Other current assets</TaxLineName>
            </TaxLineInfoRet>
            <CashFlowClassification>Operating</CashFlowClassification>
            </AccountRet>
            </AccountAddRs>
            </QBXMLMsgsRs>
        </QBXML>
"""

def test_parse_error():
    t = string_to_xml(error)
    assert isinstance(check_status(t), list)
    assert check_status(t)[0] == "Error"
    

def test_parse_success():
    s = string_to_xml(success)
    assert isinstance(check_status(s), list)
    assert check_status(s)[0] == "Info"
    
    
    
    
