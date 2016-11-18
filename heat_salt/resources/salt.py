
import requests
import os

try:
    from heat.common.i18n import _
except ImportError:
    pass

from heat.engine import resource

try:
    from heat.openstack.common import log as logging
except ImportError:
    from oslo_log import log as logging

logger = logging.getLogger(__name__)


class SaltResource(resource.Resource):

    @property
    def salt_master_url(self):
        return '%s://%s:%s' % (self.properties.get(self.SALT_PROTO),
                               self.properties.get(self.SALT_HOST),
                               self.properties.get(self.SALT_PORT))

    def login(self):
        url = os.path.join(self.salt_master_url, 'login')
        headers = {'Accept': 'application/json'}
        payload = {
            'username': self.properties[self.SALT_USER],
            'password': self.properties[self.SALT_PASSWORD],
            'eauth': 'pam'
        }

        self.login = requests.post(url, headers=headers, data=payload)
