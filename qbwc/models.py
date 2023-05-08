from datetime import datetime
from uuid import uuid4

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password

from django.contrib.contenttypes.models import ContentType


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ServiceAccount(TimeStampedModel):
    """
    Service account for the Quickbooks file.

    Generates a `.qwc` config to be installed to the QBWC. The name
    corresponds to the name of the application or integration goal.
    File path provides the option to ensure we're updating
    or querying the correct QuickBooks file. If a file moves, or is renamed, this would
    prevent the request from making any breaking changes.

    Per QBWC, the url of the calling app must be:
        - https://
        - localhost

    QBID is the guid of the user the QBWC will try to auth before accpeting a ticket.

    """

    app_name = models.CharField(max_length=30)
    app_url = models.CharField(max_length=150, default="http://localhost:8000")
    app_description = models.CharField(max_length=30)
    qbid = models.CharField(max_length=60, default=uuid4, editable=False)
    app_owner_id = models.CharField(max_length=60, default=uuid4, editable=False)
    app_file_id = models.CharField(max_length=60, default=uuid4, editable=False)
    file_path = models.CharField(max_length=150, blank=True, null=True)
    # URL of the application making requests
    # UUID included in the QBWC.qwc
    password = models.CharField(max_length=120, default="test")
    is_active = models.BooleanField(default=True)
    config = models.TextField(null=True, blank=True)

    def create_qwc_file(
        self,
        app_name="",
        url="",
        app_description="",
        username="",
        app_owner_id="",
        app_file_id="",
        sync_time=60,
    ):
        return f"""<?xml version='1.0' encoding='UTF-8'?>
            <QBWCXML>
                <AppName>{app_name}</AppName>
                <AppID></AppID>
                <AppURL>{url}/webconnector/</AppURL>
                <AppDescription>{app_description}</AppDescription>
                <AppSupport>{url}/support/</AppSupport>
                <UserName>{username}</UserName>
                <OwnerID>{{{app_owner_id}}}</OwnerID>
                <FileID>{{{app_file_id}}}</FileID>
                <QBType>QBFS</QBType>
                <Scheduler>
                    <RunEveryNMinutes>{sync_time}</RunEveryNMinutes>
                </Scheduler>
        </QBWCXML>
        """

    def authenticate(self, password):
        return check_password(password, self.password)

    def save(self, *args, **kwargs):
        self.config = self.create_qwc_file(
            app_name=self.app_name,
            url=self.app_url,
            app_description=self.app_description,
            username=self.qbid,
            app_owner_id=self.app_owner_id,
            app_file_id=self.app_file_id,
        )
        self.password = make_password(self.password)
        super(ServiceAccount, self).save(*args, **kwargs)

    def __str__(self):
        return self.app_name

    class Meta:
        verbose_name = "Service Account"
        verbose_name_plural = "Service Acounts"


class TicketManager(models.Manager):
    "Manages work to be preformed by QBWC"

    def check_approved_tickets(self) -> bool:
        "Called during authentication; determines whether new work is available."
        return self.filter(status=Ticket.TicketStatus.APPROVED).count() > 0

    def get_next_ticket(self) -> str:
        "Called during authentication; returns the next ticket in the stack."
        return self.filter(status=Ticket.TicketStatus.APPROVED).first()


class Ticket(TimeStampedModel):
    class TicketStatus(models.TextChoices):
        "Give the opportunity to review data transfers before they happen"
        CREATED = ("200", "Created")
        APPROVED = ("204", "Approved")
        PROCESSING = ("300", "Processing")
        SUCCESS = ("201", "Success")
        FAILED = ("500", "Failed")

    batch_id = models.CharField(max_length=60, default=uuid4, editable=False)
    ticket = models.CharField(max_length=60, default=uuid4, editable=False)
    status = models.CharField(
        max_length=3, choices=TicketStatus.choices, default=TicketStatus.CREATED
    )
    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    process = TicketManager()

    def check_unbatched_tasks(self):
        """Check the related entities (reverse fk lookup) for unbatched work"""
        return self.tasks.filter(batch_status=Task.BatchStatus.UN_BATCHED).count() > 0

    def get_task(self):
        """Returns an instance of dependant task"""
        return (
            self.tasks.filter(batch_status=Task.BatchStatus.UN_BATCHED)
            .order_by("-created_on")
            .first()
        )

    def processing(self):
        "View method: update ticket status to processing"
        self.status = Ticket.TicketStatus.PROCESSING
        self.save()

    def success(self):
        "View method: update ticket status to success"
        self.status = Ticket.TicketStatus.SUCCESS
        self.save()

    def failed(self):
        "View method: update ticket status to failed"
        self.status = Ticket.TicketStatus.FAILED
        self.save()

    def get_completion_status(self):
        return int(
            self.tasks.filter(batch_status=Task.BatchStatus.BATCHED).count()
            / self.tasks.all().count()
        )

    def __str__(self):
        return str(self.ticket)


class Task(TimeStampedModel):
    "Wrapper around app transactions that to affect change or action in QB"

    class TaskMethod(models.TextChoices):
        GET = (
            "GET",
            "GET",
        )
        POST = (
            "POST",
            "POST",
        )
        PATCH = (
            "PATCH",
            "PATCH",
        )
        VOID = (
            "VOID",
            "VOID",
        )
        DELETE = (
            "DELETE",
            "DELETE",
        )

    class BatchStatus(models.TextChoices):
        BATCHED = ("BATCHED", "BATCHED")
        UN_BATCHED = ("UN_BATCHED", "UN_BATCHED")

    batch_status = models.CharField(
        max_length=20, choices=BatchStatus.choices, default=BatchStatus.UN_BATCHED
    )
    batch_id = models.CharField(max_length=60, null=True)

    method = models.CharField(
        max_length=6, choices=TaskMethod.choices, default=TaskMethod.GET
    )
    model = models.CharField(max_length=90)
    ticket = models.ForeignKey(Ticket, related_name="tasks", on_delete=models.CASCADE)
    model_instance = models.ForeignKey(
        "BaseObjectMixin", null=True, on_delete=models.CASCADE
    )

    def get_model(self):
        """
        Tickets get models. Dependant tasks get assigned ticket numbers.
        Filter the dependant unbatched tasks by querying the model using the ticket number.
        """
        content_type = ContentType.objects.get(model=self.model.lower())
        model = content_type.model_class()
        return model

    def get_request(self):
        "An instance of task.."
        qbxml = ""
        if self.model_instance:
            pass
        # if self.method == self.TaskMethod.GET:
        #     qbxml = self.get_model().get()
        # elif self.ticket_id.method == self.ticket_id.TicketMethod.POST:
        #     qbxml = self.post()
        # else:
        #     qbxml = self.patch()
        qbxml = self.get_model()().request(self.method)
        return qbxml

    def process_response(self, *args, **kwargs):
        "An instance of a task"

        if self.model_instance:
            pass
        else:
            self.get_model()().process(self.method, *args, **kwargs)
            self.batch_status = Task.BatchStatus.BATCHED
            self.batch_id = self.ticket.batch_id
            self.save()


class BaseObjectMixin(TimeStampedModel):
    "Base object mixing that associated dependent models with their tickets"

    batch_id = models.CharField(max_length=60, blank=True, null=True)
    # task = models.ForeignKey(, related_name='task', blank=True, null=True, on_delete=models.SET_NULL)

    # Quickbooks Fields: if the model creates or modifies a QB transaction sync the two
    qb_list_id = models.CharField(max_length=120, blank=True, null=True)
    qb_time_created = models.DateTimeField(blank=True, null=True)
    qb_time_modified = models.DateTimeField(blank=True, null=True)

    def request(self, method, *args, **kwargs):
        raise NotImplemented

    def process(self, method, *args, **kwargs):
        raise NotImplemented

    def get():
        raise NotImplemented

    def post():
        raise NotImplemented

    def patch():
        raise NotImplemented

    def void():
        raise NotImplemented

    def delete():
        raise NotImplemented

    def process_get():
        raise NotImplemented

    def process_post():
        raise NotImplemented

    def process_patch():
        raise NotImplemented

    def process_delete():
        raise NotImplemented
