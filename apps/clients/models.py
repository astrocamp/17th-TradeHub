from django.db import models
from django_fsm import FSMField, transition


class Client(models.Model):
    name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=150)
    email = models.EmailField()
    create_at = models.DateTimeField(auto_now_add=True)
    delete_at = models.DateTimeField(auto_now=True)
    note = models.TextField(null=True, max_length=150)

    def __str__(self):
        return self.name

    CLIENT_STATE_OFTEN = "often"
    CLIENT_STATE_HAPLY = "haply"
    CLIENT_STATE_NEVER = "never"

    CLIENT_STATE_CHOICES = [
        (CLIENT_STATE_OFTEN, "經常"),
        (CLIENT_STATE_HAPLY, "偶爾"),
        (CLIENT_STATE_NEVER, "從不"),
    ]

    state = FSMField(
        default=CLIENT_STATE_NEVER,
        choices=CLIENT_STATE_CHOICES,
        protected=True,
    )

    def update_state(self):
        pass

    @transition(field=state, source="*", target=CLIENT_STATE_NEVER)
    def set_never(self):
        pass

    @transition(field=state, source="*", target=CLIENT_STATE_HAPLY)
    def set_haply(self):
        pass

    @transition(field=state, source="*", target=CLIENT_STATE_OFTEN)
    def set_often(self):
        pass

    def add_state(self):
        pass

    def remove_state(self):
        pass
