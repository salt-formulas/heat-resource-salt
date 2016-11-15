
import requests

try:
    from heat.common.i18n import _
except ImportError:
    pass

from heat.engine import attributes
from heat.engine import properties

try:
    from heat.openstack.common import log as logging
except ImportError:
    from oslo_log import log as logging

from heat_salt.resources import salt

logger = logging.getLogger(__name__)


class SaltMetadata(salt.SaltResource):

    PROPERTIES = (
        SALT_HOST, SALT_PORT, SALT_PROTO, SALT_USER, SALT_PASSWORD, NAME, CLASSES, PARAMETERS
    ) = (
        'salt_host', 'salt_port', 'salt_proto', 'salt_user', 'salt_password', 'name', 'classes', 'parameters'
    )

    properties_schema = {
        SALT_HOST: properties.Schema(
            properties.Schema.STRING,
            _('Salt Master API address.'),
            update_allowed=False,
            required=True,
        ),
        SALT_PORT: properties.Schema(
            properties.Schema.STRING,
            _('Salt Master API port.'),
            update_allowed=False,
            default='8000',
            required=True,
        ),
        SALT_PROTO: properties.Schema(
            properties.Schema.STRING,
            _('Salt Master API protocol.'),
            update_allowed=False,
            default='http',
            required=True,
        ),
        SALT_USER: properties.Schema(
            properties.Schema.STRING,
            _('Salt master user name.'),
            update_allowed=False,
            default='admin',
            required=True,
        ),
        SALT_PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('Salt user password.'),
            update_allowed=False,
            required=True,
        ),
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Managed server name.'),
            update_allowed=False,
            required=True,
        ),
        CLASSES: properties.Schema(
            properties.Schema.STRING,
            _('Managed server classes.'),
            update_allowed=False,
            required=True,
        ),
        PARAMETERS: properties.Schema(
            properties.Schema.STRING,
            _('Managed server parameters.'),
            update_allowed=False,
            required=True,
        ),
    }

    attributes_schema = {
        "name": attributes.Schema(
            _('Name of the host.'),
        ),
        "classes": attributes.Schema(
            _('Classes assigned to the node.'),
        ),
        "parameters": attributes.Schema(
            _('Optional parameters of the node.'),
        ),
    }


    def handle_create(self):
        self.login()
        self.name = self.properties.get(self.NAME)

        headers = {'Accept': 'application/json'}
        
        payload = {
            'fun': 'key.gen_accept',
            'client': 'wheel',
            'tgt': '*',
            'match': self.name
        }

        request = requests.post(
            self.salt_master_url, headers=headers,
            data=payload, cookies=self.login.cookies)

        keytype = request.json()['return'][0]['data']['return']
        if keytype:
            for key, value in keytype.items():
                if value[0] == self.registered_name:

                    self.data_set('private_key', value[1], redact=True)
                    self.data_set('name', self.value[0])

                    self.resource_id_set(self.name)

                    return True
                    break
                else:
                    raise Exception('{} does not match!'.format(key))
        else:
            raise Exception(
                '{} key does not exist in master until now...'.format(keytype))


    def _show_resource(self):
        return self.data()


    def handle_delete(self):

        self.login()

        logger.error("Could not delete node %s metadata", self.resource_id)


def resource_mapping():
    return {
        'Salt::Minion::Metadata': SaltMetadata,
    }
