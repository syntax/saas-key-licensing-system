from api import Database
import random

def createLicense():
    def generatekey(random_chars=32, alphabet="0123456789abcdefghijklmnopqrstuvwxyz"):
        r = random.SystemRandom()
        return ''.join([r.choice(alphabet) for i in range(random_chars)])

    while True:
        license = generatekey()
        conn = Database()
        if conn.checkIfLicenseExists(license):
            continue
        else:
            print(f'created license {license}')
            conn.commitLicense(license)
            conn.closeConnection()
            return license



db = Database()
db.checkIfLicenseBound('gnwi0oyzuad5wixv1a8mw962xkxb5lzx')
for _ in range(4):
    createLicense()