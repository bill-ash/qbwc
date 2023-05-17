from django.db import models

from qbwc.models import BaseObjectMixin, Task
from qbwc.utils import parse_time_stamp
from qbwc.parser import string_to_xml, parse_query_element


class GlAccount(BaseObjectMixin):
    class GLAccountType(models.TextChoices):
        AP = (
            "AccountsPayable",
            "AccountsPayable",
        )
        AR = (
            "AccountsReceivable",
            "AccountsReceivable",
        )
        BANK = (
            "Bank",
            "Bank",
        )
        COGS = (
            "CostOfGoodsSold",
            "CostOfGoodsSold",
        )
        CREDIT_CARD = (
            "CreditCard",
            "CreditCard",
        )
        EQUITY = (
            "Equity",
            "Equity",
        )
        EXPENSE = ("Expense", "Expense")
        FIXED_ASSET = (
            "FixedAsset",
            "FixedAsset",
        )
        INCOME = (
            "Income",
            "Income",
        )
        LONG_TERM_LIABILITY = (
            "LongTermLiability",
            "LongTermLiability",
        )
        NON_POSTING = (
            "NonPosting",
            "NonPosting",
        )
        OTHER_ASSET = (
            "OtherAsset",
            "OtherAsset",
        )
        OTHER_CURRENT_ASSET = (
            "OtherCurrentAsset",
            "OtherCurrentAsset",
        )
        OTHER_CURRENT_LIABILITY = (
            "OtherCurrentLiability",
            "OtherCurrentLiability",
        )
        OTHER_EXPENSE = (
            "OtherExpense",
            "OtherExpense",
        )
        OTHER_INCOME = (
            "OtherIncome",
            "OtherIncome",
        )

    # Mirror QB attributes
    name = models.CharField(max_length=120, unique=True)
    full_name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, null=True)
    account_type = models.CharField(max_length=50, choices=GLAccountType.choices)
    account_number = models.CharField(max_length=40, unique=False)
    mark_for_delete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Application info
    help_name = models.CharField(max_length=30, blank=True, null=True)
    help_description = models.TextField(blank=True, null=True)

    # Limit which accounts are displayed in the application to choose from
    display = models.BooleanField(default=True)

    def request(self, method):
        """
        Write the requests that make the most sense for your application.
        """
        if method == Task.TaskMethod.GET:
            return """
                <?qbxml version="15.0"?>
                    <QBXML>
                    <QBXMLMsgsRq onError="stopOnError">
                        <AccountQueryRq requestID="1">
                            <ActiveStatus>All</ActiveStatus> 
                        </AccountQueryRq>
                    </QBXMLMsgsRq>
                </QBXML>
            """

        if method == Task.TaskMethod.POST:
            return f"""
                <?qbxml version="16.0"?>
                <QBXML>
                <QBXMLMsgsRq onError="stopOnError">
                    <AccountAddRq>
                        <AccountAdd> 
                            <Name >{self.name}</Name> 
                            <AccountType >{self.account_type}</AccountType> 
                            <AccountNumber >{self.account_number}</AccountNumber>
                            <Desc >{self.description}</Desc>
                        </AccountAdd>
                    </AccountAddRq>
                </QBXMLMsgsRq>
                </QBXML>
                """
        if method == Task.TaskMethod.DELETE:
            # <!-- ListDelType may have one of the following values: Account, BillingRate, Class, Currency, Customer, CustomerMsg, CustomerType, DateDrivenTerms, Employee, InventorySite, ItemDiscount, ItemFixedAsset, ItemGroup, ItemInventory, ItemInventoryAssembly, ItemNonInventory, ItemOtherCharge, ItemPayment, ItemSalesTax, ItemSalesTaxGroup, ItemService, ItemSubtotal, JobType, OtherName, PaymentMethod, PayrollItemNonWage, PayrollItemWage, PriceLevel, SalesRep, SalesTaxCode, ShipMethod, StandardTerms, ToDo, UnitOfMeasureSet, Vehicle, Vendor, VendorType, WorkersCompCode -->
            return f"""
            <?qbxml version="16.0"?>
            <QBXML>
                <QBXMLMsgsRq onError="stopOnError">
                    <ListDelRq>      
                        <ListDelType>Account</ListDelType>
                        <ListID>{self.qbwc_list_id}</ListID>
                   </ListDelRq>
            </QBXMLMsgsRq>
            </QBXML>
            """

    def process(self, method, response, *args, **kwargs):
        """
        Response handler:
            Write custom logic tailored to your application.
            - Returns an instance of GlAccount?
        """
        try:
            if method == Task.TaskMethod.GET:
                rs = string_to_xml(response)
                for rs in rs.iter("AccountQueryRs"):
                    for q in rs.iter("AccountRet"):
                        account = parse_query_element(q)
                        GlAccount.objects.update_or_create(
                            # Account names must be unique
                            name=account["Name"],
                            defaults={
                                "qbwc_list_id": account["ListID"],
                                "full_name": account["FullName"],
                                "description": account.get("Desc", ""),
                                "account_type": account["AccountType"],
                                "account_number": account.get("AccountNumber", ""),
                                "qbwc_time_created": parse_time_stamp(
                                    account["TimeCreated"]
                                ),
                                "qbwc_time_modified": parse_time_stamp(
                                    account["TimeModified"]
                                ),
                            },
                        )

            if method == Task.TaskMethod.POST:
                rs = string_to_xml(response)
                for rs in rs.iter("AccountAddRs"):
                    for q in rs.iter("AccountRet"):
                        account = parse_query_element(q)
                        self.qbwc_list_id = account["ListID"]
                        self.qbwc_time_created = parse_time_stamp(
                            account["TimeCreated"]
                        )
                        self.qbwc_time_modified = parse_time_stamp(
                            account["TimeModified"]
                        )
                        self.save()

            if method == Task.TaskMethod.DELETE:
                # response = """<?xml version="1.0" ?>
                # <QBXML>
                # <QBXMLMsgsRs>
                # <ListDelRs statusCode="0" statusSeverity="Info" statusMessage="Status OK">
                # <ListDelType>Account</ListDelType>
                # <ListID>8000006C-1702682914</ListID>
                # <TimeDeleted>2023-12-15T22:06:12-05:00</TimeDeleted>
                # <FullName>New Account Name</FullName>
                # </ListDelRs>
                # </QBXMLMsgsRs>
                # </QBXML>
                # """

                rs = string_to_xml(response)
                account = parse_query_element(rs)
                self.name = f"DEL_{account['ListDelRsFullName']}_{account['ListDelRsTimeDeleted']}"
                self.full_name = f"DEL_{account['ListDelRsFullName']}_{account['ListDelRsTimeDeleted']}"
                self.qbwc_time_modified = parse_time_stamp(
                    account["ListDelRsTimeDeleted"]
                )
                self.is_active = False
                self.display = False
                self.save()

        except Exception as e:
            raise KeyError(e) from e

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "GL Account"
        verbose_name_plural = "GL Accounts"


class OtherNameList(BaseObjectMixin):
    name = models.CharField(max_length=60)
