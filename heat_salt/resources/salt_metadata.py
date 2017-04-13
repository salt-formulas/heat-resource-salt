
import six
import uuid
import requests
import json

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


class SaltMinionMetadata(salt.SaltResource):

    PROPERTIES = (
        SALT_HOST, SALT_PORT, SALT_PROTO, SALT_USER, SALT_PASSWORD, NAME, CLASSES, PARAMETERS
    ) = (
        'salt_host', 'salt_port', 'salt_proto', 'salt_user', 'salt_password', 'name', 'classes', 'parameters'
    )

    ATTRIBUTES = (
        NAME, CLASSES, PARAMETERS,
    ) = (
        'name', 'classes', 'parameters'
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
            _('Managed server name.'),
            update_allowed=False,
            required=True,
        ),
        CLASSES: properties.Schema(
            properties.Schema.LIST,
            _('Managed server classes.'),
            update_allowed=False,
            required=True,
        ),
        PARAMETERS: properties.Schema(
            properties.Schema.MAP,
            _('Managed server parameters.'),
            update_allowed=False,
            required=False,
        ),
    }

    attributes_schema = {
        NAME: attributes.Schema(
            _('Name of the server.'),
            type=attributes.Schema.STRING
        ),
        CLASSES: attributes.Schema(
            _('Classes assigned to the server.'),
            type=attributes.Schema.LIST
        ),
        PARAMETERS: attributes.Schema(
            _('Custom parameters of the server.'),
            type=attributes.Schema.MAP
        ),
    }

    def _show_resource(self):
        return self.data()

    def _resolve_attribute(self, key):
        return self.data().get(key, None)

    def handle_create(self):
        self.login()
        headers = {'Accept': 'application/json'}
        payload = {
            'fun': 'reclass.node_create',
            'client': 'local',
            'tgt': '*',
            'arg': [
                self.properties.get(self.NAME),
                '_generated',
                'default',
                'prd',
                json.dumps(self.properties.get(self.CLASSES)),
                json.dumps(self.properties.get(self.PARAMETERS))
            ]
        }

        logger.info(payload)

        request = requests.post(
            self.salt_master_url, headers=headers,
            data=payload, cookies=self.login.cookies)

        self.data_set('name', self.properties.get(self.NAME))
        self.data_set('classes', json.dumps(self.properties.get(self.CLASSES)))
        self.data_set('parameters', json.dumps(
            self.properties.get(self.PARAMETERS)))
        self.resource_id_set(six.text_type(uuid.uuid4()))

    def handle_delete(self):
        headers = {'Accept': 'application/json'}
        payload = {
            'fun': 'reclass.node_delete',
            'client': 'local',
            'tgt': '*',
            'arg': [
                self.properties.get(self.NAME),
            ],
        }

        try:
            self.login()
            request = requests.post(self.salt_master_url,
                                    headers=headers,
                                    data=payload,
                                    cookies=self.login.cookies)
        except Exception:
            pass

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass


def resource_mapping():
    return {
        'OS::Salt::MinionMetadata': SaltMinionMetadata,
    }
