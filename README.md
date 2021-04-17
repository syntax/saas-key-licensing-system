HOW TO RUN PROGRAM

------

An example database has been set-up for the purpose of showcase. Use the following login details to access different aspects of the application.

For the admin panel, use account
user: admin
password: test

For the user's point of view, use accounts
user: windows4life or appleman22 or johnsmith2
password: ExamplePassword123!!

------
HOW TO RUN LOCALLY:::

requirements;
- Python 3.7, should work on Python 3.+
- the following python libs; Flask, flask-login, flask-limiter, requests, matplotlib

following cmd commands will install required libraries:
pip install Flask
pip install flask-login
pip install Flask-Limiter
pip install requests
pip install matplotlib

AFTER THIS, config.json needs to be edited in order to correspond with the directory the program is being run in.

After all requirements have been met, running main.py will run the host server on your localhost machine.

------
ALTERNATIVELY:::

Can also be accessed remotely @ http://178.62.24.189:5000/, application is currently running on a ubunutu server at this address.

Host application has the same example showcase database set up, so feel free to login with any of the accounts

If you wish to run the example client described in the testing elements of the documentation, navigate to exampleclient/client.py in the code base and run the following file. A license key also needs to be entered into exampleclient/userconfig.json, this can be retrieved through login as one of the above provided accounts.

This shows client-server model working etc.

PLEASE NOTE: server has very little processing power, code has not been written for this server, and deployment on this server was not thorough. It should represent client-server model working, however for a real showcase of the web application and host program, please run locally. After brief testing on the server-hosted application, some functions like image rendering were not working as expected due to above reasons.

-----
