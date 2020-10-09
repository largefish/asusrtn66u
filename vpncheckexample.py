#This example script can be used with the asusrtn66u Python class to check if the VPN connection is working
#and, if not, reboot the router to bring the VPN back up

#It is very specific to my environment and probably won't work for you out of the box
#It is included to give you an idea of some things you can do

import smtplib
import requests
import time
from datetime import datetime

import asusrtn66u

#Send an email with information that needs to be seen
def emailnotify(subject, body):
    fromaddress = "" 
    toaddress  = ""

    msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (fromaddress, toaddress, subject,  body)

    #Make a Yahoo email account and set up app login for the account to send yourself emails
    #from it
    username = ""
    password = ""

    server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddress, toaddress, msg)
    server.quit()    

def getexternalip():
    r = requests.get("http://icanhazip.com")
    externalip = r.text
    return externalip

#This will log the results of the VPN check in a log file and keep the past 24 hours of check results
def log(externalip, entry):
    #Path to your log file
    logfile = ""

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    f = open(logfile, "a")
    f.write(now + " " + entry + "\n")
    f.close()

    with open(logfile, "r") as f:
        rows = f.readlines()
    f.close()

    #Cron runs this script every 15 minutes. 96 lines is 24 hours of logs
    if len(rows) > 96:
        rows = rows[-96:]
        f = open(logfile, "w")
        for r in rows:
            f.write(r)
        f.close()

#The login address and credentials for the router itself
loginURL = "https://192.168.1.1:8443"
username = ""
password = ""

#My naked IP when the VPN is down. If this is my IP, VPN is not up
nakedip = ""


try:
    externalip = getexternalip()
except Exception as e:
    if "Remote end closed connection without response" in str(e):
        body = "Curl closed with an error: " + str(e)
        log("none", body)
        exit()

    else:    
        router = asusrtn66u.rtn66u(loginURL, username, password)
        router.loginrouter()
        router.rebootrouter()

        subject = "Router messed up :-/"
        body = "The below error was thrown. The router was rebooted\n\n" + str(e)
        emailnotify(subject, body)
        log("none", body) 
        exit()

externalip = externalip.strip()

#VPN is down. Reboot!
if externalip == nakedip:
    router = asusrtn66u.rtn66u(loginURL, username, password)
    router.loginrouter()
    router.rebootrouter()

    subject = "VPN Was Down :-/"
    body = "The external IP " + externalip + " appeared to be a naked IP so the router was rebooted"
    emailnotify(subject, body)

#Enter your known good VPN IP here
elif externalip.startswith(""):
    subject = "VPN All Good"
    body = "IP appears to be up"
    #emailnotify(subject, body)

#Not only is VPN down, the internet connection is not working. Reboot!
elif "curl: (6) Could not resolve host: icanhazip.com" in externalip:
    router = asusrtn66u.rtn66u(loginURL, username, password)
    router.loginrouter()
    router.rebootrouter()

    subject = "Router messed up :-/"
    body = "Curl could not resolve its requested domain, indicating that the internet wasn\'t working. The router was rebooted"
    emailnotify(subject, body)

#If IP is different from VPN or naked, send an email to investigate further
else:
    subject = "VPN Changed"
    body = "The external IP " + externalip + " is not recognized as the naked or VPN IP. You should check it out."
    emailnotify(subject, body)
    
log(externalip, body)
