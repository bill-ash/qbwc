from qbwc.models import Ticket, Task, ServiceAccount

service = ServiceAccount()
service.app_name = "QBWC Data Sync"
service.app_url = "http://localhost:8000"
service.app_description = "Django QuickBooks WebConnector"
service.qbid = "511829ea-f359-43cb-a885-844ebd8aabb1"
service.app_owner_id = "63293baf-fc64-4747-afa4-3fb5861c9f48"
service.app_file_id = "5d7eef11-6f07-4bc6-9c01-b911a6597f96"
service.save()

# ServiceAccount.objects.all()
Ticket.objects.all().delete()
Task.objects.all().delete()

# Create a ticket for a get request
ticket = Ticket()
ticket.status = Ticket.TicketStatus.APPROVED
ticket.save()

task = Task()
task.ticket = ticket
task.model = "GlAccount"
task.method = Task.TaskMethod.GET
task.model_instance = None
task.save()

# Check for new work
Ticket.process.check_approved_tickets()
response = Ticket.process.get_next_ticket()

t = Ticket.objects.get(ticket=response)

# Show all the dependent tasks
t.check_unbatched_tasks()
t.get_completion_status()
work = t.get_task()
work.get_model()
work.get_request()


# The ticket will always have a task: reverse lookup the task by the ticket


# Check for new Work
# Check for new tickets
TicketQueue.process.check_approved_tickets()

# Get the next ticket
ticket = TicketQueue.process.get_next_ticket()

# Call the xml from the ticket: returns an instance of ticket
tick = TicketQueue.objects.get(ticket=ticket)
