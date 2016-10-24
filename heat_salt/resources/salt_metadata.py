
import requests

try:
    from heat.common.i18n import _
except ImportError:
    pass

from heat.engine import properties

try:
    from heat.openstack.common import log as logging
except ImportError:
    from oslo_log import log as logging

from .salt_auth import SaltAuth

logger = logging.getLogger(__name__)


class SaltMetadata(SaltAuth):

    PROPERTIES = (
        SALT_HOST, SALT_USER, SALT_PASSWORD, HOSTNAME, CLASSES, PARAMETERS

    ) = (
        'salt_host', 'user', 'password', 'hostname'
    )

    ATTRIBUTES = (
        PRIVATE_KEY, REGISTERED_NAME
    ) = (
        'classes', 'parameters'
    )

    properties_schema = {
        SALT_HOST: properties.Schema(
            properties.Schema.STRING,
            _('Salt Master Host'),
            update_allowed=False,
            required=True,
        ),
        USER: properties.Schema(
            properties.Schema.STRING,
            _('Salt user'),
            update_allowed=False,
            default='admin',
            required=True,
        ),
        PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('Salt password'),
            update_allowed=False,
            required=True,
        ),
        HOSTNAME: properties.Schema(
            properties.Schema.STRING,
            _('Hostname'),
            update_allowed=False,
            required=True,
        )
    }

    attributes_schema = {
        "classes": _("Classes assigned to the node."),
        "parameters": _("Optional parameters of the node."),
    }

    update_allowed_keys = ('Properties',)

    def handle_create(self):

        self.login()

        self.registered_name = '.'.join([
            self.properties[self.HOSTNAME],
            self.properties[self.DOMAIN]])

        headers = {'Accept': 'application/json'}
        accept_key_payload = {
            'fun': 'key.gen_accept',
            'client': 'wheel',
            'tgt': '*',
            'match': self.registered_name
        }

        request = requests.post(
            self.salt_master_url, headers=headers,
            data=accept_key_payload,
            cookies=self.login.cookies)

        keytype = request.json()['return'][0]['data']['return']
        if keytype:
            for key, value in keytype.items():
                if value[0] == self.registered_name:

                    self.data_set('private_key', value[1], redact=True)
                    self.data_set('registered_name', self.value[0])

                    self.resource_id_set(self.registered_name)

                    return True
                    break
                else:
                    raise Exception('{} does not match!'.format(key))
        else:
            raise Exception(
                '{} key does not exist in master until now...'.format(keytype))

    def _resolve_attribute(self, name):
        if name == 'classes':
            return self.data().get('classes')
        if name == 'parameters':
            return self.data().get('parameters')

    def handle_delete(self):

        self.login()

        logger.error("Could not delete node %s", self.resource_id)


def resource_mapping():
    return {
        'Salt::Minion::Key': SaltMetadata,
    }
