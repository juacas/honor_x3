import logging
import base64
import re
import json
import hashlib
from requests import session \

from . import crypto

_LOGGER = logging.getLogger(__name__)


class HonorX3Client:
    def __init__(self, host, username, password):
        """Initialize the client."""
        self.statusmsg = None
        self.host = host
        self.username = username
        self.password = password
        self.session = None
        self.login_data = None
        self.status = 'off'
        self.device_info = None

    # REBOOT THE ROUTER
    def reboot(self) -> bool:
        if not self.login:
            return False
        # REBOOT REQUEST
        _LOGGER.info("Requesting reboot")
        try:
            data = {
                'csrf': {'csrf_param': self.login_data['csrf_param'], 'csrf_token': self.login_data['csrf_token']}}
            r = self.session.post('https://{0}/api/service/reboot.cgi'.format(self.host),
                                  data=json.dumps(data, separators=(',', ':')))
            data = json.loads(re.search('({.*?})', r.text).group(1))
            assert data['errcode'] == 0, data
            _LOGGER.info("Rebooting HG659")
            return True
        except Exception as e:
            _LOGGER.error('Failed to reboot: {0} with data {1}'.format(e, data))
            return False
        finally:
            self.logout()

    # LOGIN PROCEDURE
    def login(self) -> bool:
        """
        Login procedure using SCRAM challenge
        :return: true if the login has succeeded
        """
        pass_hash = hashlib.sha256(self.password.encode()).hexdigest()
        pass_hash = base64.b64encode(pass_hash.encode()).decode()
        # INITIAL CSRF

        try:
            self.session = session()
            r = self.session.get('https://{0}/api/system/deviceinfo'.format(self.host), verify=False)
            self.status = 'on'
            device_info = r.json()

            assert device_info['csrf_param'] and device_info['csrf_token'], 'Empty csrf_param or csrf_token'
        except Exception as e:
            _LOGGER.error('Failed to get CSRF. error "{0}" '.format(e))
            self.statusmsg = e.errorCategory
            self.status = 'off'
            return False

        ## LOGIN ##
        try:
            pass_hash = self.username + pass_hash + \
                        device_info['csrf_param'] + device_info['csrf_token']
            firstnonce = hashlib.sha256(pass_hash.encode()).hexdigest()
            data = {'csrf': {'csrf_param': device_info['csrf_param'],
                             'csrf_token': device_info['csrf_token']},
                    'data': {'username': self.username, 'firstnonce': firstnonce}}
            r = self.session.post('https://{0}/api/system/user_login_nonce'.format(self.host),
                                  data=json.dumps(data, separators=(',', ':')), verify=False)
            responsenonce = r.json()
            salt = responsenonce['salt']
            servernonce = responsenonce['servernonce']
            iterations = responsenonce['iterations']
            client_proof = crypto.get_client_proof(firstnonce, servernonce, self.password, salt,
                                                   iterations).decode('UTF-8')

            data = {'csrf': {'csrf_param': responsenonce['csrf_param'],
                             'csrf_token': responsenonce['csrf_token']},
                    'data': {'clientproof': client_proof,
                             'finalnonce': servernonce}
                    }
            r = self.session.post('https://{0}/api/system/user_login_proof'.format(self.host),
                                  data=json.dumps(data, separators=(',', ':')), verify=False)
            loginproof = r.json()

            assert loginproof['err'] == 0
            # _LOGGER.debug("Logged in")
            self.login_data = loginproof
            self.statusmsg = None
            return True
        except Exception as e:
            _LOGGER.error('Failed to login: {0}'.format(e))
            self.statusmsg = 'Failed login: {0}'.format(e)
            self.login_data = None
            self.session.close()
            return False

    ## LOGOUT ##
    def logout(self):
        try:
            if self.login_data is None:
                return False
            data = {'csrf': {
                'csrf_param': self.login_data['csrf_param'],
                'csrf_token': self.login_data['csrf_token']
            }
            }
            r = self.session.post('https://{0}/api/system/user_logout'.format(
                self.host), data=json.dumps(data, separators=(',', ':')), verify=False)
            data = r.json()
            assert r.ok, r
            _LOGGER.debug("Logged out")
        except Exception as e:
            _LOGGER.error('Failed to logout: {0}'.format(e))
        finally:
            self.session.close()
            self.login_data = None

    def get_devices_response(self):
        """Get the raw string with the devices from the router."""
        # GET DEVICES RESPONSE
        try:
            query = 'https://{0}/api/system/HostInfo'.format(self.host)
            r = self.session.get(query, verify=False)
            devices = r.json()
            self.statusmsg = 'OK'
        except Exception as e:
            _LOGGER.error('Failed to get Devices: {0} with query {1} rdev {2}'.format(e, query, r))
            self.statusmsg = e.errorCategory
            return False
        return devices
