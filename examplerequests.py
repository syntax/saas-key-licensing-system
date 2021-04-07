import requests
from uuid import getnode as get_mac
import socket
import platform

API_KEY = ''


# Authentication class acts as a framework for building your authnetication system off

class Authentication():
    def __init__(self, licenseid):
        self.license = licenseid
        self.hwid = None
        self.devicename = None
        self.isBoundToUser = False

        self.headers = {'api_key': API_KEY}

        self.getLicenseInfo()

    def getLicenseInfo(self):
        try:
            resp = requests.get(f'http://127.0.0.1:5000/api/v1/licenses/{self.license}', headers=self.headers).json()
            self.hwid = resp['license']['HWID']
            self.devicename = resp['license']["device"]
            self.isBoundToUser = bool(resp['license']["boundToUser"])
            return resp['license']
        except:
            self.license = None
            return None

    def setToBound(self, hwid, devicename):
        payloadjson = {
            "HWID": f"{hwid}",
            "device": f"{devicename}"
        }
        resp = requests.post(f'http://127.0.0.1:5000/api/v1/licenses/{self.license}', headers=self.headers,
                             json=payloadjson).json()
        return resp

    def setToUnbound(self):
        payloadjson = {
            "HWID": None,
            "device": None
        }
        resp = requests.post(f'http://127.0.0.1:5000/api/v1/licenses/{self.license}', headers=self.headers,
                             json=payloadjson).json()
        return resp


# Local functions  (to follow) should be built in whatever way the developer sees fit, i.e. should derive the "HWID" element in a unique way, not necessarily the example shown.
# more device related data can be collected using external libararys like psutil, which can be isntalled via pip, however for the sake of example the libraries used are preinstalled with py
# These functions should be implemented around the developers software they are wanting to distrubute in order to validate users.

def collectLocalData():
    # this function will end uo being called often for comparison, and could be written in a variety of ways

    def deriveHWID():
        mac_address = get_mac()  # gets device MAC address
        processor_arch = platform.uname().processor  # gets name of local microprocessor
        machine = platform.uname().machine  # gets instruction set architecture

        return str(mac_address) + processor_arch + machine  # any convolution of relevant data would be valid, could be hashed, hashed with a pepper, etc.

    hwid = deriveHWID()
    devicename = socket.gethostname()  # gets name of local node

    return hwid, devicename


def validateUser(license):
    # this function will end uo being called often, ideally at key function within the developers program, and could be written in a variety of ways
    # this authenticates a users license to be valid, and not currently

    auth = Authentication(license)
    localhwid, localdevname = collectLocalData()

    if auth.license and auth.isBoundToUser:
        # checks license key is still valid
        if not (auth.hwid and auth.devicename):
            # in the case where license is currently unbound
            auth.setToBound(localhwid, localdevname)
        else:
            if auth.hwid == localhwid and auth.devicename == localdevname:
                # proceed with operation, license still valid
                pass
            else:
                # license is bound to another machine, not the one it is attempting to be used on, hence quit program
                quit()
    else:
        # license key is invalid, hence quit progam
        quit()
