
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


class SaltAuth(resource.Resource):

    @property
    def salt_master_url(self):
        return '%s://%s:8000' % (self.properties.get(self.SALT_HOST_PROTOCOL),
                                 self.properties[self.SALT_HOST])

    def login(self):

        headers = {'Accept': 'application/json'}
        login_payload = {
            'username': self.properties[self.USERNAME],
            'password': self.properties[self.PASSWORD],
            'eauth': 'pam'
        }

        self.login = requests.post(
            os.path.join(self.salt_master_url,
                         'login'), headers=headers, data=login_payload)
