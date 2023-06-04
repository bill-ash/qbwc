from pathlib import Path
from qbwc.parser import (
    string_to_xml,
    parse_query_element,
    parse_table_elems,
    check_status,
)


def read_test_xml(obj):
    xml_path = Path().absolute()
    with open(xml_path / f"tests/test_data/{obj}.xml", "r") as xml:
        return xml.read()


def test_parser():
    accounts = read_test_xml("accounts")
    root = string_to_xml(accounts)
    data_list = []
    for account_rs in root.iter("AccountQueryRs"):
        data_list.extend(parse_query_element(q) for q in account_rs.iter("AccountRet"))

    assert len(data_list) == 116


def test_customer_parser():
    customers = read_test_xml("customers")
    root = string_to_xml(customers)
    elems = parse_table_elems(root, "CustomerRet")
    assert len(elems) == 146

    # elems[10]
    # r = pd.json_normalize(elems)
    # r.to_clipboard()


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
    assert isinstance(check_status(t), str)
    assert check_status(t) == "Error"


def test_parse_success():
    s = string_to_xml(success)
    assert isinstance(check_status(s), str)
    assert check_status(s) == "Info"
