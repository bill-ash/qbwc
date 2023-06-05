from django.db import models

from qblists.models import OtherNameList
from accounts.models import GlAccount

from qbwc.models import BaseObjectMixin, Task
from qbwc.decorators import string_escape_decorator

from qbwc.parser import string_to_xml, parse_table_elems, parse_time_stamp, truthy

from qbwc.exceptions import QBXMLProcessingError


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
    vendor = models.ForeignKey(OtherNameList, on_delete=models.CASCADE)
    account = models.ForeignKey(GlAccount, on_delete=models.CASCADE)

    date = models.DateField()
    reference_number = models.CharField(max_length=12)
    memo = models.CharField(max_length=80)
    description = models.TextField()
    amount = models.FloatField()

    qbwc_txn_number = models.CharField(max_length=120)

    # vendor = models.ForeignKey(CreditCardVendor, blank=True, null=True, on_delete=models.CASCADE)
    # \\TODO: needs more research:
    # https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey("content_type", "object_id")
    # vendor = GenericForeignKey("content_type", "object_id")
    # I can then add a GenericRelation field to the models that will most likely be used as vendors
    # to access the orm
    # credit_card_vendor = GenericRelation(CreditCardCharge, related_query_name='vendor')

    @string_escape_decorator
    def request(self, method, *args, **kwargs):
        if method == Task.TaskMethod.POST:
            return f"""
                <?qbxml version="15.0"?>
                    <QBXML>
                    <QBXMLMsgsRq onError="stopOnError">
                        <CreditCardChargeAddRq>
                            <CreditCardChargeAdd> 
                            <AccountRef>                                         
                                <FullName>{self.credit_card}</FullName>
                            </AccountRef>

                            <PayeeEntityRef>
                                <FullName >{self.vendor}</FullName>
                            </PayeeEntityRef>
                            
                            <TxnDate >{self.date}</TxnDate> 
                            <RefNumber >{self.reference_number}</RefNumber>
                            <Memo >{self.memo}</Memo> 
                            
                            <ExpenseLineAdd> 
                                <AccountRef> 
                                    <FullName >{self.account}</FullName>
                                </AccountRef>
                                <Amount >{self.amount}</Amount> 
                                <Memo >{self.description}</Memo> 
                            </ExpenseLineAdd>
                                    
                            </CreditCardChargeAdd>
                    </CreditCardChargeAddRq>
                    </QBXMLMsgsRq>
                    </QBXML>
                """

    def process(self, method, response, *args, **kwargs):
        # {
        #     "AccountRefListID": "570000-1071509253",
        #     "AccountRefFullName": "QuickBooks Credit Card",
        #     "ExpenseLineRetTxnLineID": "2B1A1-1734309938",
        #     "ExpenseLineRetAmount": "100.12",
        #     "ExpenseLineRetMemo": "This is a description of the expense...",
        #     "PayeeEntityRefListID": "800000E2-1734240481",
        #     "PayeeEntityRefFullName": "w cas!df467",
        #     "TxnID": "2B19F-1734309938",
        #     "TimeCreated": "2024-12-15T19:45:38-05:00",
        #     "TimeModified": "2024-12-15T19:45:38-05:00",
        #     "EditSequence": "1734309938",
        #     "TxnNumber": "1786",
        #     "TxnDate": "2023-06-05",
        #     "Amount": "100.12",
        #     "RefNumber": "0973d7",
        #     "Memo": "Hello, world!",
        # }
        try:
            if method == Task.TaskMethod.POST:
                rs = string_to_xml(response)
                charge = parse_table_elems(rs, "CreditCardChargeRet")
                if isinstance(charge, list):
                    charge = charge[0]

                self.qbwc_list_id = charge["ExpenseLineRetTxnLineID"]
                self.qbwc_txn_number = charge["TxnNumber"]
                self.qbwc_time_created = parse_time_stamp(charge["TimeCreated"])
                self.qbwc_time_modified = parse_time_stamp(charge["TimeModified"])
                self.save()
        except Exception as e:
            raise QBXMLProcessingError(e) from e

    def __str__(self):
        return self.credit_card.name
