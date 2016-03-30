
import requests
import os

try:
    from heat.common.i18n import _
except ImportError:
    pass

from heat.engine import resource
from heat.engine import constraints
from heat.engine import properties

import base64

try:
    from heat.openstack.common import log as logging
except ImportError:
    from oslo_log import log as logging

from chef import ChefAPI, Node, Client

logger = logging.getLogger(__name__)

class SaltMinion(resource.Resource):

    PROPERTIES = (
        SALT_HOST, USER, PASSWORD, HOSTNAME, DOMAIN, RUN_LIST, ENVIRONMENT, DOMAIN_PREPEND_TENANT_NAME

    ) = (
        'chef_host', 'user', 'password', 'hostname', 'domain', 'run_list', 'environment', 'domain_prepend_tenant_name'
    )

    ATTRIBUTES = (
        PRIVATE_KEY, REGISTERED_NAME
    ) = (
        'private_key', 'registered_name'
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
            _('Server hostname'),
            update_allowed=False,
            required=True,
        ),
        DOMAIN: properties.Schema(
            properties.Schema.STRING,
            _('Server domainname'),
            update_allowed=False,
            required=True,
        ),
        RUN_LIST: properties.Schema(
            properties.Schema.STRING,
            _('Node run list'),
            update_allowed=True,
            required=False,
        ),
        ENVIRONMENT: properties.Schema(
            properties.Schema.STRING,
            _('Chef environment'),
            update_allowed=True,
            required=True,
        ),
        DOMAIN_PREPEND_TENANT_NAME: properties.Schema(
            properties.Schema.BOOLEAN,
            _('Prepend tenant name to domain name'),
            update_allowed=False,
            required=True,
        ),
    }

    attributes_schema = {
        "private_key": _("Private key of the node."),
        "registered_name": _("FQDN of registered node ."),
    }

    update_allowed_keys = ('Properties',)


    def __init__(self, name, json_snippet, stack):
        super(SaltMinion, self).__init__(name, json_snippet, stack)

    def _login():

        url = 'https://%s:8000' % self.properties[self.SALT_HOST]
        headers = {'Accept':'application/json'}
        login_payload = {
            'username': self.properties[self.USERNAME],
            'password': self.properties[self.PASSWORD],
            'eauth':'pam'
        }

        self.login = requests.post(os.path.join(url, 'login'), headers=headers, data=login_payload)

    def handle_create(self):

        self._login()
    
        self.registered_name = self.properties[self.HOSTNAME]+"."+ self.properties[self.DOMAIN]

        headers = {'Accept':'application/json'}
        accept_key_payload = {
            'fun': 'key.gen_accept',
            'client':'wheel',
            'tgt':'*',
            'match': self.registered_name
        }

        request = requests.post(url,headers=headers,data=accept_key_payload,cookies=self.login.cookies)

        keytype = request.json()['return'][0]['data']['return']
        if keytype:
            for key,value in keytype.items():
                if value[0] == self.registered_name:

                    self.data_set('private_key', value[1], redact=True)
                    self.data_set('registered_name', self.value[0])

                    self.resource_id_set(self.registered_name)

                    return True
                    break
                else:
                    raise Exception('{} does not match!'.format(keyname))
        else:
            raise Exception('{} key does not exist in master until now...'.format(keyname)) 
            
    def _resolve_attribute(self, name):
        if name == 'private_key':
            return self.data().get('private_key')
        if name == 'registered_name':
            return self.data().get('registered_name')

    def handle_delete(self):

        self._login()

        logger.error("Could not delete node %s", self.resource_id)

def resource_mapping():
    return {
        'OS::Salt::Minion': SaltMinion,
    }
