from api import Database
import random
import hashlib
import csv
import matplotlib

#necessary in relation to imports as to stop
matplotlib.use('Agg')

import matplotlib.pyplot as plt

def generatekey(random_chars, alphabet="abcdefghijklmnopqrstuvwxyz1234567890"):
    r = random.SystemRandom()
    return ''.join([r.choice(alphabet) for _ in range(random_chars)])


def createLicense(planname):
    initialconn = Database()
    if initialconn.getPlanInfo(planname):
        initialconn.closeConnection()
        while True:
            license = generatekey(random_chars=16)
            # 79586 6110994640 0884391936 combinations
            conn = Database()
            if conn.checkIfLicenseExists(license):
                continue
            else:
                print(f'created license {license}')
                conn.commitLicense(license, planname)
                conn.closeConnection()
                return license
    else:
        initialconn.closeConnection()
        return 'Plan does not exist'


def gensalt(username):
    # a strange algorithm to create larger salts, as well as remove the predictability vulnerability for as long as this algorithm is kept secret
    def ceaser(shift, string):
        alphabet = '0abcdefghijkl1234mnopqrst567uvwx89yz'
        output = []

        for letter in string:
            if letter.strip() and letter in alphabet:
                output.append(alphabet[(alphabet.index(letter) + shift) % 36])

        return ''.join(output)

    def manipulationalgo(inputstr):
        doubled = ''.join([element * 2 for element in inputstr])
        output = []
        count = 1
        for letter in doubled:
            # cant use .index() as letter appears multiple times!
            if count % 2 == 0:
                output.append(ceaser(count, letter))
            else:
                output.append(ceaser(-1, letter))
            count += 1

        return ''.join(output)

    salt = manipulationalgo(username)
    pepper = '3UwF4zVIB2CkF3uOMkmAifCMjO+88RKNfL4u6EXifPQ='

    return salt + pepper


def hash(username, password):
    hashdpw = hashlib.pbkdf2_hmac(
        hash_name='sha256',  # The hash digest algorithm for HMAC
        password=password.encode('utf-8'),
        salt=gensalt(username).encode('utf-8'),
        iterations=100000  # 100,000 iterations of SHA-256
    )

    return hashdpw.hex()


def createAdminUser(values):
    # needs username,fName,sName,emailAddress,password passed into it as a comma seperated str, where pw is pre hashed
    values += ',TRUE'
    db = Database()
    db.addToUsers(values)
    return 'success'


def gatherStatistics():
    db = Database()

    #this dict can easily be added to due to modular programming design
    try:
        dict = {
            "Licenses": db.getCountofTable('licenses'),
            "Users": db.getCountofTable('users'),
            "Plans": db.getCountofTable('plans'),
            "Users with a License Bound": db.getConditionalCountofTable('licenses','boundToUser','1'),
            "Licenses Bound to a User's Device": db.getConditionalCountofTable('licenses', 'boundToDevice', '1'),
            "Most Popular Plan": db.getMostPopular('licenses','plan')[0],
            "Percentages of Licenses bound to a User": f'''{round((db.getConditionalCountofTable('licenses','boundToUser','1')/ db.getCountofTable('licenses'))*100, 2)}%'''
                }
    except:
        # in the case where tables are not populated enough
        dict = {
            "Licenses": '',
            "Users": '',
            "Plans":'',
            "Users with a License Bound": '',
            "Licenses Bound to a User's Device": '',
            "Most Popular Plan": '',
            "Percentages of Licenses bound to a User": '',
        }

    db.closeConnection()
    return dict

def generateGraph():
    with open('graphinfo.csv','r') as graphdata:
        graphpoints = csv.reader(graphdata, delimiter=',')
        rows = list(graphpoints)

    # get licenses graph
    fig, ax = plt.subplots()
    if len(rows) > 15:
        plt.plot([value[0] for value in rows[1:][-15:]], [int(value[1]) for value in rows[1:][-15:]])
    else:
        plt.plot([value[0] for value in rows[1:]], [int(value[1]) for value in rows[1:]])
    plt.ylabel(rows[0][1])
    fig.autofmt_xdate()
    plt.savefig('static/images/licenses.png',dpi=300)

    # get users graph
    fig, ax = plt.subplots()
    if len(rows) > 15:
        plt.plot([value[0] for value in rows[1:][-15:]], [int(value[2]) for value in rows[1:][-15:]])
    else:
        plt.plot([value[0] for value in rows[1:]], [int(value[2]) for value in rows[1:]])
    plt.ylabel(rows[0][2])
    fig.autofmt_xdate()
    plt.savefig('static/images/users.png', dpi=300)


if __name__ == '__main__':
    generateGraph()
    createAdminUser(f'''admin,tom,holland,admin@gmail.com,{hash('admin', 'test')}''')

