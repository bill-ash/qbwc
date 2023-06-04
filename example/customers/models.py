from django.db import models

from qbwc.models import BaseObjectMixin, Task
from qbwc.parser import string_to_xml, parse_table_elems, parse_time_stamp


class Customer(BaseObjectMixin):
    """
    Important: We highly recommend that you use the 
    IncludeRetElement tag in your CustomerQuery to
    include any data you want but do NOT include the 
    ShipAddress data in the Response, unless you need
    to get the shipping address for a particular customer.
    Excluding the shipping address data will significantly 
    improve the performance of the CustomerQuery.
    """

    name = models.CharField(max_length=120, blank=True, null=True)
    company_name = models.CharField(max_length=60)
    first_name = models.CharField(max_length=60, blank=True, null=True)
    last_name = models.CharField(max_length=60, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display = models.BooleanField(default=True)

    def request(self, method, *args, **kwargs):
        # Select specific elements to speed up queries using the <IncludeRetElement> tag 
        if method == Task.TaskMethod.GET:
            return """
                <?qbxml version="16.0"?>
                <QBXML>
                <QBXMLMsgsRq onError="stopOnError">
                    <CustomerQueryRq requestID="1">
                        <ActiveStatus>All</ActiveStatus> 
                            <IncludeRetElement >ListID </IncludeRetElement >
                            <IncludeRetElement >TimeCreated </IncludeRetElement >
                            <IncludeRetElement >TimeModified </IncludeRetElement >
                            <IncludeRetElement >Name </IncludeRetElement >
                            <IncludeRetElement >FullName </IncludeRetElement >
                            <IncludeRetElement >FirstName </IncludeRetElement >
                            <IncludeRetElement >LastName </IncludeRetElement >
                            <IncludeRetElement >CompanyName </IncludeRetElement >
                            <IncludeRetElement >IsActive </IncludeRetElement >
                            <IncludeRetElement >Sublevel </IncludeRetElement >
                    </CustomerQueryRq>
                </QBXMLMsgsRq>
            </QBXML>
        """

    def process(self, method, response, *args, **kwargs):
        """
        {
            'AdditionalNotesRetNoteID': '0',
            'AdditionalNotesRetDate': '2011-07-27',
            'AdditionalNotesRetNote': 'Use "Overhead" for expenses that aren\'t related to a specific Customer:Job',
            'SalesTaxCodeRefListID': '10000-999022286',
            'SalesTaxCodeRefFullName': 'Tax',
            'BillAddressBlockAddr1': 'Overhead',
            'BillAddressAddr1': 'Overhead',
            'ListID': '800000B0-1197755238',
            'TimeCreated': '2007-12-15T16:47:18-05:00',
            'TimeModified': '2023-12-16T00:06:44-05:00',
            'EditSequence': '1702703204',
            'Name': 'Overhead',
            'FullName': 'Overhead',
            'IsActive': 'true',
            'Sublevel': '0',
            'Balance': '0.00',
            'TotalBalance': '0.00',
            'JobStatus': 'None',
            'Notes': 'Use "Overhead" for expenses that aren\'t related to a specific Customer:Job',
            'PreferredDeliveryMethod': 'None'
        }
        """
        if method == Task.TaskMethod.GET:
            rs = string_to_xml(response)
            customers = parse_table_elems(rs, "CustomerRet")
            for customer in customers:
                # filter for parent customers only
                # Unset entity attributes will not be returned when syncing with QB
                # Ensure sensible defaults are chosen for your application
                if customer['Sublevel'] == '0':
                    Customer.objects.update_or_create(
                        qbwc_list_id=customer["ListID"],
                        defaults={
                            "name": customer["Name"],
                            # "company_name": customer["CompanyName"],
                            # Will fail when no CompanyName is set for the Customer
                            "company_name": customer.get("CompanyName", ""),
                            "first_name": customer.get("FirstName", ""),
                            "last_name": customer.get("LastName", ""),
                            "qbwc_time_created": parse_time_stamp(customer["TimeCreated"]),
                            "qbwc_time_modified": parse_time_stamp(customer["TimeModified"]),
                        },
                    )


    def __str__(self):
        return self.name