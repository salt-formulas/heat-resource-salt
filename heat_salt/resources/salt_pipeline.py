
import six
import uuid
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


class SaltPipeline(salt.SaltResource):

    PROPERTIES = (
        SALT_HOST, SALT_PORT, SALT_PROTO, SALT_USER, SALT_PASSWORD, CREATE_PIPELINE, DELETE_PIPELINE,
    ) = (
        'salt_host', 'salt_port', 'salt_proto', 'salt_user', 'salt_password', 'create_pipeline', 'delete_pipeline'
    )

    ATTRIBUTES = (
        CREATE_OUTPUT, DELETE_OUTPUT,
    ) = (
        'create_output', 'delete_output',
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
        CREATE_PIPELINE: properties.Schema(
            properties.Schema.LIST,
            _('Create handle pipeline.'),
            update_allowed=False,
            required=True,
        ),
        DELETE_PIPELINE: properties.Schema(
            properties.Schema.LIST,
            _('Delete handle pipeline.'),
            update_allowed=False,
            required=True,
        ),
    }

    attributes_schema = {
        CREATE_OUTPUT: attributes.Schema(
            _('Create handle pipeline output.'),
            type=attributes.Schema.STRING
        ),
        DELETE_OUTPUT: attributes.Schema(
            _('Delete handle pipeline output.'),
            type=attributes.Schema.STRING
        ),
    }

    def _show_resource(self):
        return self.data()

    def _resolve_attribute(self, key):
        return self.data().get(key, None)

    def handle_create(self):
        self.login()
        headers = {'Accept': 'application/json'}
        output = []
        for step in self.properties.get(self.CREATE_PIPELINE):
            payload = {
                'client': 'local',
                'tgt': step.get('tgt'),
                'fun': step.get('fun'),
                'arg': step.get('arg'),
            }
            request = requests.post(self.salt_master_url, headers=headers,
                                    data=payload, cookies=self.login.cookies)
            data = request.json()['return'][0]['data']['return']
            output.append(data)
        self.data_set('create_output', '\n'.join(str(output)))
        self.resource_id_set(six.text_type(uuid.uuid4()))

    def handle_delete(self):
        self.login()
        headers = {'Accept': 'application/json'}
        output = []
        for step in self.properties.get(self.DELETE_PIPELINE):
            payload = {
                'client': 'local',
                'tgt': step.get('tgt'),
                'fun': step.get('fun'),
                'arg': step.get('arg'),
            }
            request = requests.post(self.salt_master_url, headers=headers,
                                    data=payload, cookies=self.login.cookies)
            data = request.json()['return'][0]['data']['return']
            output.append(data)
        self.data_set('delete_output', '\n'.join(str(output)))


    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass


def resource_mapping():
    return {
        'OS::Salt::Pipeline': SaltPipeline,
    }
