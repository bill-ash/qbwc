import logging

from django.shortcuts import render
from spyne.decorator import rpc, srpc
from spyne.model.complex import Array, Unicode
from spyne.model.primitive import Integer, String
from spyne.service import ServiceBase

from qbwc.app_settings import QBWC_CODES, QBWC_VERSION
from qbwc.parser import string_to_xml, check_status
from qbwc.models import ServiceAccount, Ticket

logger = logging.getLogger("django")


class QuickBooksService(ServiceBase):
    @srpc(Unicode, Unicode, _returns=Array(Unicode))
    def authenticate(strUserName, strPassword):
        """
        Authenticate with QuickBooks WebConnector.
        Return value schedule:
         - No work to be preformed:
            - ['none', 'none']
         - Pending request: session token of work to reference and the current open company file
            - ['guid', '']
            - ['guid', 'path/to/file_name.qbo']
         - Invalid user - not authenticated
            - ['', ''] | ['nvu', 'nvu']

        Args:
        @rpc >> ctx (DjangoHttpMethodContext): spyne.server.django.DjangoHttpMethodContext Inspect the information
        returned to be parsed by spyne from the webconnector.
        The ctx (djangoHttpMethodContext) returns the method call of the webconnector as well as the parsed xml
            strUsername (str): Username to authenticate against. Needs to match realm id passed
            when creating qbwc app installed.
            strPassword (str): Password to match against realm password
        """
        try:
            account = ServiceAccount.objects.get(qbid=strUserName)
            assert account.authenticate(strPassword)

            if Ticket.process.check_approved_tickets():
                ticket = Ticket.process.get_next_ticket()
                logger.info(f"Ticket Submitted: {ticket.ticket}")
                ticket.processing
                return [ticket.ticket, QBWC_CODES.CURRENT_COMPANY]
            else:
                logger.info("No tickets in queue...")
                return [QBWC_CODES.NONE, QBWC_CODES.NONE]

        except Exception as e:
            logger.error(f"Invalid user: {e}")
            return [QBWC_CODES.INVALID_USER, QBWC_CODES.INVALID_USER]

    @srpc(Unicode, Unicode, Unicode, Unicode, Integer, Integer, _returns=String)
    def sendRequestXML(
        ticket,
        strHCPResponse,
        strCompanyFileName,
        qbXMLCountry,
        qbXMLMajorVers,
        qbXMLMinorVers,
    ):
        """
        Send QBXML to the QBWC.

        Args:
            ticket (_type_): _description_
            strHCPResponse (_type_): _description_
            strCompanyFileName (_type_): _description_
            qbXMLCountry (_type_): _description_
            qbXMLMajorVers (_type_): _description_
            qbXMLMinorVers (_type_): _description_

        Returns:
            _type_: _description_
        """
        logger.info("sendRequestXML() has been called")
        logger.info(f"ticket: {ticket}")

        ticket = Ticket.objects.get(ticket=ticket)

        try:
            # Iterates through tasks looking for any incomplete tasks
            work = ticket.get_task()
            qbxml = work.get_request()
        except Exception:
            logger.error(f"Error processing request {ticket}")
            return ""
        logger.info(f"Processing ticket: {ticket}")
        logger.info(f"Sending request: {qbxml}")

        return qbxml

    @srpc(Unicode, Unicode, Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ticket, response, hresult, message):
        """
        Returns the data response form the QuickBooks WebConnector.

        Not all errors generate hex messages.

        Args:
            ticket (str): ticket
            response (QBXML): Response from QuickBooks
            hresult (str): Hex error message that could accompany any successful work
            message (str): Error message

        @return (int) Positive integer 100 for completed work, and less than 100 to move to the next ticket.
            Needs to be handled by the session manager.
        """
        logger.info("receiveResponseXML() has been called")
        logger.info(f"ticket={ticket}")
        logger.info(f"response={response}")
        logger.info(f"hresult={hresult}")
        logger.info(f"message={message}")

        return_value = 0

        try:
            str_response = string_to_xml(response)
            response_status = check_status(str_response)
            assert response_status != "Error"
        except Exception as e:
            logger.error(f"hresult={hresult}")
            logger.error(f"message={message}")
            return -101

        if len(hresult) > 0:
            # Handle errors that happen before processing
            logger.error(f"hresult={hresult}")
            logger.error(f"message={message}")
            return -101

        ticket = Ticket.objects.get(ticket=ticket)
        task = ticket.get_task()

        try:
            task.process_response(response, message)
        except Exception as e:
            logger.error(f"Failed to process response: {e}")
            return -1

        return_value = ticket.get_completion_status()

        if return_value == 100:
            ticket.success

        return return_value

    @srpc(Unicode, _returns=Unicode)
    def serverVersion(strVersion, *args):
        """
        Provide a way for web-service to notify web connector of it’s version and other details about version
        @param ticket the ticket from web connector supplied by web service during call to authenticate method
        @return string message string describing the server version and any other information that user may want to see
        """
        version = QBWC_VERSION
        logger.info(f"getServerVersion(): version={version}")
        return version

    @srpc(Unicode, _returns=Unicode)
    def clientVersion(strVersion, *args, **kwargs):
        """
        Check the current WebConnector version is compatiable with the application.

        Args:
            strVersion (str): QBWC Version
        """
        if strVersion == QBWC_VERSION:
            logger.info("Matches current version")
        logger.info(f"clientVersion(): version={strVersion}")

        return QBWC_CODES.CURRENT_VERSION

    @rpc(Unicode, _returns=Unicode)
    def closeConnection(ctx, ticket):
        """
        Close the current connection with QuickBooks Webconnector.
        This is where we can clean up any work

        Args:
            ctx (DjangoHttpMethodContext): spyne processed request wasdl
            ticket (str): ticket that is completed?
        """
        logger.info(f"closeConnection(): ticket={ticket}")
        return f"Completed Operation: {ticket}"

    @srpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def connectionError(ticket, hresult, message):
        """
        Tell the web service about an error the web connector encountered in its attempt to connect to QuickBooks
        or QuickBooks POS
        @param ticket the ticket from web connector supplied by web service during call to authenticate method
        @param hresult the HRESULT (in HEX) from the exception thrown by the request processor
        @param message The error message that accompanies the HRESULT from the request processor
        @return string value "done" to indicate web service is finished or the full path of the different company for
        retrying _set_connection.
        """
        logger.error(
            f"connectionError(): ticket={ticket}, hresult={hresult}, message={message}"
        )
        ticket = Ticket.objects.get(ticket=ticket)
        ticket.failed
        return QBWC_CODES.CONN_CLOSE_ERROR

    @srpc(Unicode, _returns=Unicode)
    def getLastError(ticket):
        """
        Allow the web service to return the last web service error, normally for displaying to user, before
        causing the update action to stop.
        @param ticket the ticket from web connector supplied by web service during call to authenticate method
        @return string message describing the problem and any other information that you want your user to see.
        The web connector writes this message to the web connector log for the user and also displays it in the web
        connector’s Status column.
        """
        logger.error(f"getLastError(): ticket={ticket}")
        ticket = Ticket.objects.get(ticket=ticket)
        ticket.failed
        return f"Error processing ticket: {ticket}"


def support(request):
    return render(request, "qbwc/support.html")
