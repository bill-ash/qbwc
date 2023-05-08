import logging

from datetime import datetime
from lxml import etree
from uuid import uuid4

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.conf import settings

from spyne.decorator import rpc, srpc
from spyne.model.complex import Array, Unicode
from spyne.model.primitive import Integer, String
from spyne.service import ServiceBase

# Error handling:
# - Return an empty string in the sendRequestXML
# - Return a negative number in the receiveResponseXML
# - Both will call getLastError()

# from qbwc.objects import process_response, process_query_response
from qbwc.app_settings import QBWC_CODES, QBWC_VERSION
from qbwc.models import (
    ServiceAccount,
    Ticket,
    Task,
)

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
                ticket.processing()
                return [ticket.ticket, QBWC_CODES.CURRENT_COMPANY]
            else:
                logger.info("No tickets in queue...")
                return [QBWC_CODES.NONE, QBWC_CODES.NONE]

            # return [QBWC_CODES.NONE, QBWC_CODES.NONE]

        except Exception as e:
            logger.error(f"Invalid user: {e}")
            return [QBWC_CODES.INVALID_USER, QBWC_CODES.INVALID_USER]

    @srpc(
        Unicode, Unicode, Unicode, Unicode, Integer, Integer, _returns=String
    )  # Unicode, Unicode, Unicode,
    def sendRequestXML(
        ticket,
        strHCPResponse,
        strCompanyFileName,
        qbXMLCountry,
        qbXMLMajorVers,
        qbXMLMinorVers,
    ):
        logger.info("sendRequestXML() has been called")
        logger.info(f"ticket: {ticket}")
        logger.info(f"strCompanyFileName {strCompanyFileName}")

        ticket = Ticket.objects.get(ticket=ticket)
        work = ticket.get_task()
        qbxml = work.get_request()
        logger.info(f"Processing ticket: {ticket}")
        logger.info(f"Sending request: {qbxml}")

        return qbxml

    @srpc(Unicode, Unicode, Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ticket, response, hresult, message):
        """
        Returns the data response form the QuickBooks WebConnector.

        Args:
            ticket (str): ticket
            response (QBXML): Response from QuickBooks
            hresult (str): Hex error message that could accompany any successful work
            message (str): Error message

        @return (int) Positive integer 100 for completed work, and less than 100 to move to the next ticket.
            Needs to be handled by the session manager.
        """

        logger.info("receiveResponseXML()")
        logger.info(f"ticket={ticket}")
        logger.info(f"response={response}")
        logger.info(f"hresult={hresult}")
        logger.info(f"message={message}")

        return_value = 0

        if len(hresult) > 0:
            logger.error(f"hresult={hresult}")
            logger.error(f"message={message}")
            # triggers lastErrror() callback
            return_value = -101
        else:
            ticket = Ticket.objects.get(ticket=ticket)
            work = ticket.get_task()
            work.process_response(response, message)
            return_value = ticket.get_completion_status()

            if return_value == 100:
                ticket.success()
        return return_value

        # current_ticket = TicketQueue.objects.get(ticket=ticket)
        # model = current_ticket.get_model()

    #         try:
    #             # Process the response from QuickBooks - should this be model dependent?
    #             # response_code = process_response(response).get("statusSeverity")
    #             qb_response = process_query_response(response)

    #         except Exception as e:
    #             logger.error(str(e))
    #             current_ticket.status = TicketQueue.TicketStatus.FAILED
    #             current_ticket.save()
    #             raise KeyError("Error processing response from QB")

    #         if current_ticket.method == current_ticket.TicketMethod.GET:
    #             try:
    #                 # Assumes GET method is a single round trip...
    #                 logger.debug("Processing GET query response")

    #                 model.process_get(qb_response, ticket)
    #                 current_ticket.status = current_ticket.TicketStatus.SUCCESS
    #                 current_ticket.save()

    #             except Exception as e:
    #                 logger.error(str(e))
    #                 current_ticket.status = current_ticket.TicketStatus.FAILED
    #                 current_ticket.save()
    #                 raise KeyError(f"Error processing GET: {current_ticket.ticket}")

    #         elif current_ticket.method == current_ticket.TicketMethod.POST:
    #             try:
    #                 logger.debug("Processing POST query response")
    #                 # Errors get handled in processing function and bubble to { getLastError() }

    #                 model.process_post(qb_response, ticket)

    #                 # Move this method to the ticket...
    #                 # current_ticket.objects.filter(ticket__batch_status )
    #                 if model.process.check_for_work(current_ticket):
    #                     # if model.process.check_for_work(ticket):
    #                     logger.debug("More work to do")
    #                     return 90

    #                 else:
    #                     logger.debug("Work completed")
    #                     current_ticket.status = current_ticket.TicketStatus.SUCCESS
    #                     current_ticket.save()
    #                     return 100

    #             except Exception as e:
    #                 # Don't try to handle exception end the operation
    #                 logger.error(str(e))
    #                 # breakpoint()
    #                 current_ticket.status = current_ticket.TicketStatus.ERROR
    #                 current_ticket.save()
    #                 raise KeyError(f"Error processing POST: {current_ticket.ticket}")
    #                 # return 100
    #         else:
    #             try:
    #                 logger.debug("Processing PATCH query response")

    #             except Exception as e:
    #                 logger.error(str(e))
    #                 current_ticket.status = current_ticket.TicketStatus.ERROR
    #                 current_ticket.save()
    #                 raise KeyError(
    #                     f"Error processing patch request: {current_ticket.ticket}"
    #                 )

    #         if hresult is not None:  # response_code == "Error" or
    #             # Errors should be logged and continued upon?
    #             pass
    #         else:
    #             pass

    #         return 100

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
        # breakpoint()
        logger.info(f"closeConnection(): ticket={ticket}")
        # return QBWC_CODES.CONN_CLOSE_OK
        return f"Completed Operation: {ticket}"

    #     @srpc(Unicode, Unicode, Unicode, _returns=Unicode)
    #     def connectionError(ticket, hresult, message):
    #         """
    #         Tell the web service about an error the web connector encountered in its attempt to connect to QuickBooks
    #         or QuickBooks POS
    #         @param ticket the ticket from web connector supplied by web service during call to authenticate method
    #         @param hresult the HRESULT (in HEX) from the exception thrown by the request processor
    #         @param message The error message that accompanies the HRESULT from the request processor
    #         @return string value "done" to indicate web service is finished or the full path of the different company for
    #         retrying _set_connection.
    #         """
    #         # log = MessageLog(
    #         #     type = 'error',
    #         #     hresult = hresult,
    #         #     message = str(logger.debug(f'connectionError(): ticket={ticket}, hresult={hresult}, message={message}'))
    #         # )
    #         # log.save()

    #         logger.debug(
    #             f"connectionError(): ticket={ticket}, hresult={hresult}, message={message}"
    #         )

    #         current_ticket = TicketQueue.objects.get(ticket=ticket)
    #         current_ticket.status = TicketQueue.TicketStatus.ERROR

    #         return QBWC_CODES.CONN_CLOSE_ERROR

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
        return f"Error processing ticket: {ticket}"


def support(request):
    return render(request, "qbwc/support.html")
