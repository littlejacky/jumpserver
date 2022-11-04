from django.db import models
from django.utils.translation import ugettext_lazy as _

from common.db import fields
from common.db.models import JMSBaseModel
from assets.const import AutomationTypes, SecretType, SecretStrategy, SSHKeyStrategy
from .base import BaseAutomation

__all__ = ['ChangeSecretAutomation', 'ChangeSecretRecord']


class ChangeSecretAutomation(BaseAutomation):
    secret_type = models.CharField(
        choices=SecretType.choices, max_length=16,
        default=SecretType.password, verbose_name=_('Secret type')
    )
    secret_strategy = models.CharField(
        choices=SecretStrategy.choices, max_length=16,
        default=SecretStrategy.custom, verbose_name=_('Secret strategy')
    )
    secret = fields.EncryptTextField(blank=True, null=True, verbose_name=_('Secret'))
    password_rules = models.JSONField(default=dict, verbose_name=_('Password rules'))
    ssh_key_change_strategy = models.CharField(
        choices=SSHKeyStrategy.choices, max_length=16,
        default=SSHKeyStrategy.add, verbose_name=_('SSH key change strategy')
    )
    recipients = models.ManyToManyField('users.User', blank=True, verbose_name=_("Recipient"))

    def save(self, *args, **kwargs):
        self.type = AutomationTypes.change_secret
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Change secret automation")

    def to_attr_json(self):
        attr_json = super().to_attr_json()
        attr_json.update({
            'secret': self.secret,
            'secret_type': self.secret_type,
            'secret_strategy': self.secret_strategy,
            'password_rules': self.password_rules,
            'ssh_key_change_strategy': self.ssh_key_change_strategy,
            'recipients': {
                str(recipient.id): (str(recipient), bool(recipient.secret_key))
                for recipient in self.recipients.all()
            }
        })
        return attr_json


class ChangeSecretRecord(JMSBaseModel):
    execution = models.ForeignKey('assets.AutomationExecution', on_delete=models.CASCADE)
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, null=True)
    account = models.ForeignKey('assets.Account', on_delete=models.CASCADE, null=True)
    old_secret = fields.EncryptTextField(blank=True, null=True, verbose_name=_('Old secret'))
    new_secret = fields.EncryptTextField(blank=True, null=True, verbose_name=_('Secret'))
    date_started = models.DateTimeField(blank=True, null=True, verbose_name=_('Date started'))
    date_finished = models.DateTimeField(blank=True, null=True, verbose_name=_('Date finished'))
    status = models.CharField(max_length=16, default='pending')
    error = models.TextField(blank=True, null=True, verbose_name=_('Error'))

    class Meta:
        verbose_name = _("Change secret record")

    def __str__(self):
        return self.account.__str__()
