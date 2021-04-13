from main import Renewal
from api import Database
import utils
import time
import datetime
import csv


def monitorRenewals():
    # function that repetitively monitors for when current time becomes equal to the users license date
    # whent this event occurs, it attempts to charge the user (stub function as explained in design documentation)
    # upon success renewal date is incremeneted, upon failure key is destroyed
    while True:

        def charge(session):
            # placeholder function

            # sing session ID, makes get request to status webhook
            # creates communction with stripe API, which will return one of the following
            if session:
                event_type = "checkout.session.completed"  # response from stripe API, example.
                if event_type == "checkout.session.completed" or "invoice.paid":
                    return True
                else:
                    return False

        db = Database()
        rendict = db.getAllLicenseWithRenewal()
        db.closeConnection()
        now = datetime.datetime.now()
        for value in rendict:
            if (rendict[value] - now).total_seconds() <= 0:

                db = Database()
                session = db.getLicenseStripeSessionID(value)
                attempt = charge(session)

                if attempt:
                    renewal = Renewal(value)
                    renewal.incrementRenewalDate()
                    renewal.commitRenewdatetoDatabase(value)
                else:
                    print('failed to charge')
                    db = Database()
                    db.deleteLicense(value)
                    db.closeConnection()
            else:
                pass

        time.sleep(5)


def monitorGraphs():
    # function that monitors for when it becomes a new day
    # when this event occurs, it recollects data relating to number of users/ licenses against time
    # then polts new graphs for the admin user to see on their dashboard
    while True:

        with open('graphinfo.csv', 'r') as current_file:
            latestdate = list(csv.reader(current_file, delimiter=','))[-1][0]

        latestdate = datetime.datetime.strptime(latestdate, '%d/%m/%Y').date()
        nowdate = datetime.date.today()

        if nowdate > latestdate:
            with open('graphinfo.csv', 'a') as current_file:
                db = Database()
                current_file.write(
                    f'''\n{datetime.datetime.strftime(nowdate, '%d/%m/%Y')},{db.getCountofTable('licenses')},{db.getCountofTable('users')}''')
                db.closeConnection()

            # generate a new set of graphs for the new day
            utils.generateGraph()

        # only checks to refesh once every 10 minutes, as generating graphs is relatively processer intensive
        time.sleep(10 * 60)
