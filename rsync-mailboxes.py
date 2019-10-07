import os
import configparser

# Import configuration file with secrets
config = configparser.ConfigParser()
config.read('config.ini')

poweruser_pass = ["poweruser_password"]["password"]

with open('/etc/dovecot/maildirusers', 'r') as f:
        maildirusers = f.read().split("\n")
        for line in maildirusers:
                if line != "":
                        print(line)
                        os.system("rsync -vaz -e 'ssh -i /home/jonathanweaver/.ssh/id_rsa' ~%s/Maildir/ poweruser@cpanel-7.host.chi1.int-i.net:/home/poweruser/mail/poweruser.com/%s" % (line, line))
