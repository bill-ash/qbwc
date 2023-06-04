import pytest

from qbwc.models import Ticket


def test_ticket_status():
    ticket = Ticket()
    assert ticket.TicketStatus.CREATED
    assert ticket.TicketStatus.APPROVED
    assert ticket.TicketStatus.FAILED
    assert ticket.TicketStatus.PROCESSING


# assert Ticket.objects.first().status == "204"
# assert Task.objects.first().method == "POST"
# assert ticket.check_task_queue()
# assert Ticket.process.check_approved_tickets()
# assert Ticket.process.get_next_ticket().ticket == str(ticket.ticket)
# assert ticket.get_completion_status() == 0
# assert ticket.tasks.count() == 5
