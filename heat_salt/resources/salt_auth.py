
import requests
import os

try:
    from heat.common.i18n import _
except ImportError:
    pass

from heat.engine import resource
from heat.engine import constraints
from heat.engine import properties

try:
    from heat.openstack.common import log as logging
except ImportError:
    from oslo_log import log as logging

logger = logging.getLogger(__name__)

class SaltAuth(resource.Resource):

    def login():

        url = 'https://%s:8000' % self.properties[self.SALT_HOST]
        headers = {'Accept':'application/json'}
        login_payload = {
            'username': self.properties[self.USERNAME],
            'password': self.properties[self.PASSWORD],
            'eauth':'pam'
        }

        self.login = requests.post(os.path.join(url, 'login'), headers=headers, data=login_payload)
