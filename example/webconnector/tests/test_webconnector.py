import pytest

from qbwc.models import ServiceAccount, Task, Ticket
from django.urls import reverse


@pytest.mark.django_db
def test_view(client):
    url = reverse("support")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_service_account_create():
    service = ServiceAccount()
    service.app_name = "QBWC Data Sync"
    service.app_url = "http://localhost:8000"
    service.app_description = "Django QuickBooks WebConnector"
    service.qbid = "511829ea-f359-43cb-a885-844ebd8aabb1"
    service.app_owner_id = "63293baf-fc64-4747-afa4-3fb5861c9f48"
    service.app_file_id = "5d7eef11-6f07-4bc6-9c01-b911a6597f96"
    service.save()

    assert ServiceAccount.objects.count() == 1


@pytest.mark.django_db
def test_ticket_task_create():
    ticket = Ticket()
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.save()

    task = Task()
    task.ticket = ticket
    task.model = "GlAccount"
    task.method = Task.TaskMethod.GET
    task.model_instance = None
    task.save()

    assert Ticket.objects.count() == 1
    assert Task.objects.count() == 1
