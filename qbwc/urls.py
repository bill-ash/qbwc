from django.urls import path
from qbwc.views import support 

from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoView

urlpatterns = [
    path("support/", support, name="support"),
    # path(
    #     "webconnector/",
    #     DjangoView.as_view(
    #         services=[QuickBooksService],
    #         tns="http://developer.intuit.com/",
    #         in_protocol=Soap11(validator="lxml"),
    #         out_protocol=Soap11(),
    #     ),
    # ),
]