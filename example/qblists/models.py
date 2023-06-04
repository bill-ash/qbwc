from django.db import models
from qbwc.models import BaseObjectMixin, Task
from qbwc.parser import string_to_xml, parse_query_element, parse_time_stamp
from qbwc.decorators import string_escape_decorator


class OtherNameList(BaseObjectMixin):
    name = models.CharField(max_length=60, unique=True)

    @string_escape_decorator
    def request(self, method):
        """
        Write the requests that make the most sense for your application.
        """
        if method == Task.TaskMethod.GET:
            return """
                <?qbxml version="15.0"?>
                    <QBXML>
                    <QBXMLMsgsRq onError="stopOnError">
                        <OtherNameQueryRq requestID="1">
                            <ActiveStatus>ActiveOnly </ActiveStatus> 
                        </OtherNameQueryRq >
                    </QBXMLMsgsRq>
                </QBXML>
            """

        if method == Task.TaskMethod.POST:
            return f"""
                <?qbxml version="15.0"?>
                    <QBXML>
                    <QBXMLMsgsRq onError="stopOnError">
                        <OtherNameAddRq requestID="1">
                            <OtherNameAdd>
                                <Name>{self.name}</Name>
                            </OtherNameAdd>
                        </OtherNameAddRq >
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
                for rs in rs.iter("OtherNameQueryRs"):
                    for elm in rs.iter("OtherNameRet"):
                        other_name = parse_query_element(elm)

                        OtherNameList.objects.update_or_create(
                            qbwc_list_id=other_name["ListID"],
                            defaults={
                                "name": other_name["Name"],
                                "qbwc_time_created": parse_time_stamp(
                                    other_name["TimeCreated"]
                                ),
                                "qbwc_time_modified": parse_time_stamp(
                                    other_name["TimeModified"]
                                ),
                            },
                        )
            if method == Task.TaskMethod.POST:
                rs = string_to_xml(response)
                for rs in rs.iter("OtherNameAddRs"):
                    for elm in rs.iter("OtherNameRet"):
                        other_name = parse_query_element(elm)
                        self.qbwc_list_id = other_name["ListID"]
                        self.qbwc_time_created = parse_time_stamp(
                            other_name["TimeCreated"]
                        )
                        self.qbwc_time_modified = parse_time_stamp(
                            other_name["TimeModified"]
                        )
                        self.save()

        except Exception as e:
            raise KeyError(e) from e

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Other Names List"
        verbose_name_plural = "Other Names List"
