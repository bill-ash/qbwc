"""
TODO: more research is need on whether the additional complexity assocatied with 
generic foreign keys is worth the investment. 
"""

import pytest 
pytestmark = pytest.mark.skip(reason="Skipping entire file")

def skip(): 
    from creditcards.models import CreditCard, CreditCardCharge
    # from creditcards.models import  CreditCardVendor

    from vendors.models import Vendor 
    from qblists.models import OtherNameList

    card = CreditCard.objects.first()

    vendor = Vendor(name='hello')
    vendor.save()

    other_name = OtherNameList(name='world')
    other_name.save()

    # card_vendor = CreditCardVendor(content_object=vendor)
    # card_vendor.save()

    # card_other = CreditCardVendor(content_object=other_name)
    # card_other.save()


    charge_1 = CreditCardCharge(
        credit_card = card, 
        vendor = Vendor.objects.last(),
        description = "Charge One",
        amount = 100
    )
    charge_1.save()
    charge_1.vendor.pk


    charge_2 = CreditCardCharge(
        credit_card = card, 
        vendor = OtherNameList.objects.last(),
        description = "Charge Two",
        amount = 200
    )
    charge_2.save()


    Vendor.objects.all()
    vendor  = Vendor.objects.last()
    OtherNameList.objects.all()
    other_name = OtherNameList.objects.last()



    res = CreditCardCharge.objects.last()

    # Stores the Model Name via special: content_type
    res.content_type.name

    # Stores the Model Attributes
    res.vendor.name

    # Stores the PK
    res.object_id

    CreditCardCharge.objects.last()

    # Using the GenericRelation: reverse API lookup
    vendor.charges.all().first().amount
    other_name.charges.all().first().amount

    # The generic relation also enabels filtering and other API functions
    # Filter Credit Card Charges by a specific vendor
    CreditCardCharge.objects.filter(vendors=vendor)

    # Will not work unless the GenericRelation field is set on the related model
    CreditCardCharge.objects.filter(othernames=other_name)

    # CreditCardCharge.objects.all().delete()


