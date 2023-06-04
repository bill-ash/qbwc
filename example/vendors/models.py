from django.db import models


from qbwc.models import BaseObjectMixin, Task
from qbwc.parser import string_to_xml, parse_query_element, parse_time_stamp
from qbwc.exceptions import QBXMLProcessingError, QBXMLRequestError


class Vendor(BaseObjectMixin):
    name = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    
    help_name = models.CharField(max_length=60, blank=True, null=True)
    help_description = models.TextField(blank=True, null=True)
    display = models.BooleanField(default=True)
    """Is the record viewable in app"""
    
    

    def request(self, method, *args, **kwargs):
        """Sync vendors"""
        if method == Task.TaskMethod.GET:
            return """
                <?qbxml version="16.0"?>
                    <QBXML>
                    <QBXMLMsgsRq onError="stopOnError">
                        <VendorQueryRq requestID="1">
                        <ActiveStatus>ActiveOnly</ActiveStatus>
                        </VendorQueryRq>
                    </QBXMLMsgsRq>
                    </QBXML>
            """
        
        if method == Task.TaskMethod.POST:
            return f"""
            <?qbxml version="16.0"?>
                <QBXML>
                <QBXMLMsgsRq onError="stopOnError">
                    <VendorAddRq>
                        <VendorAdd>
                            <Name>{self.name}</Name>
                        </VendorAdd>
                    </VendorAddRq>
                </QBXMLMsgsRq>
                </QBXML>
                
        """

    def process(self, method, response, *args, **kwargs):
        """
        {
            'ContactsRetListID': '0000000000000p81',
            'ContactsRetTimeCreated': '2012-07-26T08:46:25-05:00',
            'ContactsRetTimeModified': '2012-07-26T08:46:25-05:00',
            'ContactsRetEditSequence': '1343306785', 
            'ContactsRetFirstName': 'Vivian Zeng',
            'VendorAddressBlockAddr1': 'Zeng Building Supplies',
            'VendorAddressBlockAddr2': 'Vivian Zeng',
            'VendorAddressBlockAddr3': '345 Main St.',
            'VendorAddressBlockAddr4': 'Middlefield, CA 94043',
            'VendorAddressAddr1': 'Zeng Building Supplies',
            'VendorAddressAddr2': 'Vivian Zeng',
            'VendorAddressAddr3': '345 Main St.',
            'VendorAddressCity': 'Middlefield', 
            'VendorAddressState': 'CA', 
            'VendorAddressPostalCode': '94043',
            'ListID': '800000BD-1181226959',
            'TimeCreated': '2007-06-07T10:35:59-05:00',
            'TimeModified': '2023-12-16T00:06:44-05:00',
            'EditSequence': '1702703204',
            'Name': 'Zeng Building Supplies', 
            'IsActive': 'true', 
            'CompanyName': 'Zeng Building Supplies',
            'FirstName': 'Vivian',
            'LastName': 'Zeng',
            'Contact': 'Vivian Zeng',
            'NameOnCheck': 'Zeng Building Supplies',
            'IsVendorEligibleFor1099': 'false',
            'Balance': '0.00'
        }
        """
        try:
            if method == Task.TaskMethod.GET:
                rs = string_to_xml(response)
                for rs in rs.iter("VendorQueryRs"):
                    for elm in rs.iter("VendorRet"):
                        vendor = parse_query_element(elm)
                        Vendor.objects.update_or_create(
                            qbwc_list_id=vendor["ListID"],
                            defaults={
                                "name": vendor["Name"],
                                "qbwc_time_created": parse_time_stamp(
                                    vendor["TimeCreated"],
                                ),
                                "qbwc_time_modified": parse_time_stamp(
                                    vendor["TimeModified"]
                                ),
                            },
                        )
            if method == Task.TaskMethod.POST:
                rs = string_to_xml(response)
                for rs in rs.iter("VendorAddRs"):
                    for elem in rs.iter("VendorRet"):
                        vendor = parse_query_element(elem)
                        self.qbwc_list_id - vendor["ListID"]
                        self.qbwc_time_created = parse_time_stamp(
                            vendor["TimeCreated"]
                        )
                        self.qbwc_time_modified = parse_time_stamp(
                            vendor["TimeModified"]
                        )
                        self.save()

        except Exception as e:
            QBXMLProcessingError(e)

    def __str__(self):
        return self.name
