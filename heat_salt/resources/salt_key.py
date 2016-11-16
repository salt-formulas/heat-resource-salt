
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


class MinionKey(salt.SaltResource):

    PROPERTIES = (
        SALT_HOST, SALT_PORT, SALT_PROTO, SALT_USER, SALT_PASSWORD, NAME, FORCE, KEYSIZE
    ) = (
        'salt_host', 'salt_port', 'salt_proto', 'salt_user', 'salt_password', 'name', 'force', 'keysize'
    )

    properties_schema = {
        SALT_HOST: properties.Schema(
            properties.Schema.STRING,
            _('Salt Master API address.'),
            update_allowed=False,
            required=True,
        ),
        SALT_PORT: properties.Schema(
            properties.Schema.NUMBER,
            _('Salt Master API port.'),
            update_allowed=False,
            default=8000,
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
            _('Managed server name'),
            update_allowed=False,
            required=True,
        ),
        FORCE: properties.Schema(
            properties.Schema.BOOLEAN,
            _('Force key reation'),
            update_allowed=False,
            default=False,
            required=True,
        ),
        KEYSIZE: properties.Schema(
            properties.Schema.NUMBER,
            _('Managed server key size'),
            update_allowed=False,
            default=4096,
            required=True,
        ),
    }

    attributes_schema = {
        "name": attributes.Schema(
            _('Name of the server.'),
        ),
        "private_key": attributes.Schema(
            _('Private key of the node.'),
        ),
        "public_key": attributes.Schema(
            _('Public key of the node.'),
        ),
    }


    def handle_create(self):
        self.login()
        headers = {'Accept': 'application/json'}
        payload = {
            'fun': 'key.gen_accept',
            'client': 'wheel',
            'tgt': '*',
            'id_': self.properties.get(self.NAME),
            'force': self.properties.get(self.FORCE),
            #setting up keysize raises Salt master RSA error
            #'keysize': self.properties.get(self.KEYSIZE)
        }
        request = requests.post(self.salt_master_url, headers=headers,
                                data=payload, cookies=self.login.cookies)
        data = request.json()['return'][0]['data']['return']
        if 'priv' in data and 'pub' in data:
            self.data_set('name', self.properties.get(self.NAME))
            self.data_set('private_key', data['return'][0]['data']['return']['priv'], redact=True)
            self.data_set('public_key', data['return'][0]['data']['return']['pub'])
            self.resource_id_set(self.properties.get(self.NAME))
        else:
            raise Exception('Error creating/gerating key on salt master.')


    def _show_resource(self):
        return self.data()


    def handle_delete(self):
        self.login()
        headers = {'Accept': 'application/json'}
        payload = {
            'fun': 'key.delete',
            'client': 'wheel',
            'tgt': '*',
            'match': self.properties.get(self.NAME),
        }
        request = requests.post(self.salt_master_url, headers=headers,
                                data=payload, cookies=self.login.cookies)


    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass


def resource_mapping():
    return {
        'OS::Salt::MinionKey': MinionKey,
    }
