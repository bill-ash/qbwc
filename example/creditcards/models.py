from django.db import models
from qblists.models import OtherNameList

from qbwc.models import BaseObjectMixin, Task
from qbwc.parser import (
    string_to_xml,
    parse_table_elems, 
    parse_time_stamp, 
    truthy
)

class CreditCard(BaseObjectMixin):
    name = models.CharField(max_length=60)
    full_name = models.CharField(max_length=60)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def request(self, method, *args, **kwargs):
        if method == Task.TaskMethod.GET:
            # CreditCardCreditQueryRq
            return """
                <?qbxml version="16.0"?>
                <QBXML>
                <QBXMLMsgsRq onError="stopOnError">
                    <AccountQueryRq requestID="1">
                        <ActiveStatus>ActiveOnly</ActiveStatus>
                        <AccountType>CreditCard</AccountType>
                        
                    </AccountQueryRq>
                </QBXMLMsgsRq>
            </QBXML>
        """

    def process(self, method, response, *args, **kwargs):
        if method == Task.TaskMethod.GET:
            # {
            #     "TaxLineInfoRetTaxLineID": "1577",
            #     "TaxLineInfoRetTaxLineName": "B/S-Liabs/Eq.: Other current liabilities",
            #     "ListID": "570000-1071509253",
            #     "TimeCreated": "2003-12-15T12:27:33-05:00",
            #     "TimeModified": "2023-12-16T00:06:45-05:00",
            #     "EditSequence": "1702703205",
            #     "Name": "QuickBooks Credit Card",
            #     "FullName": "QuickBooks Credit Card",
            #     "IsActive": "true",
            #     "Sublevel": "0",
            #     "AccountType": "CreditCard",
            #     "AccountNumber": "20500",
            #     "BankNumber": "5555-4444-3333-4521",
            #     "Desc": "QuickBooks Credit Card",
            #     "Balance": "293.20",
            #     "TotalBalance": "293.20",
            #     "CashFlowClassification": "Operating",
            # }
            rs = string_to_xml(response)
            cards = parse_table_elems(rs, "AccountRet")
            for card in cards:
                CreditCard.objects.update_or_create(
                    qbwc_list_id=card["ListID"],
                    defaults={
                        "name": card["Name"],
                        "full_name": card["FullName"],
                        "description": card.get("Desc", ""),
                        "is_active": truthy(card["IsActive"]),
                        "qbwc_time_created": parse_time_stamp(card["TimeCreated"]),
                        "qbwc_time_modified": parse_time_stamp(card["TimeModified"]),
                    },
                )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

# from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
# from django.contrib.contenttypes.models import ContentType

# class CreditCardVendor(models.Model):
#     """
#     Generic Foreign Key: allows a user to use the "Vendor" model or the "OtherNameList" model
#     when creating credit card charges. 
#     """
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey("content_type", "object_id")
# 
#     def __str__(self):
#         return str(self.content_type)
    

class CreditCardCharge(BaseObjectMixin): 
    credit_card = models.ForeignKey(CreditCard, on_delete=models.CASCADE)
    # vendor = models.ForeignKey(CreditCardVendor, blank=True, null=True, on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.FloatField()
    vendor = models.ForeignKey(OtherNameList, on_delete=models.CASCADE)
    
    # \\TODO: needs more research:
    # https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey("content_type", "object_id")
    # vendor = GenericForeignKey("content_type", "object_id")
    # I can then add a GenericRelation field to the models that will most likely be used as vendors 
    # to access the orm
    # credit_card_vendor = GenericRelation(CreditCardCharge, related_query_name='vendor')
    
    
    def __str__(self):
        return self.credit_card.name
    