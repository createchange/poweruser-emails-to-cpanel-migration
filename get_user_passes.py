import os
import urllib
import configparser

# Import configuration file with secrets
config = configparser.ConfigParser()
config.read('config.ini')

poweruser_pass = ["poweruser_password"]["password"]

def get_uri_encoded_pass(hashed_pass):
        return urllib.quote(hashed_pass)

with open('/etc/dovecot/maildirusers', 'r') as f:
        maildirusers = f.read().split("\n")

with open('/etc/shadow', 'r') as f:
        shadow = f.read().split("\n")

active_users = {}

for user in maildirusers:
        if user != "":
                for line in shadow:
                        split = line.split(":")
                        if user == split[0]:
                                active_users[user] = split[1]

#print(active_users)

for k,v in active_users.items():
        print(str(k) + " " + str(v))
        uri_encoded_pass = get_uri_encoded_pass(v)
        #print("uapi --user=poweruser Email add_pop email=%s password_hash=%s quota=0 domain=poweruser.com" % (k, uri_encoded_pass))
