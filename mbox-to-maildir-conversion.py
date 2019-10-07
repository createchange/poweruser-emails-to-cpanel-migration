import subprocess
from pprint import pprint
import os

def get_current_maildirusers():
    '''
    returns list of users in /etc/dovecot/maildirusers
    '''
    current_maildirusers = []

    subprocess.call("cat /etc/dovecot/maildirusers > tmp/maildirusers.txt", shell=True)
    with open("tmp/maildirusers.txt", "r") as f:
        file_contents = f.read()
        file_contents = file_contents.split("\n")
    for entry in file_contents:
        if entry != "":
            current_maildirusers.append(entry)

    return current_maildirusers


def get_non_maildirusers(current_maildirusers):
    '''
    takes current_maildirusers as input to see which accounts do not need conversion.
    cats /etc/passwd into a new file, removes existing maildirusers and creates a dict from the remaining users containing:

    k: account_name
    v: home_dir

    returns this info

    '''
    account_info = {}
    subprocess.call("cat /etc/passwd > tmp/passwd.txt", shell=True)

    with open("tmp/passwd.txt","r") as f:
        file_contents = f.read()
        file_contents = file_contents.split("\n")

    for entry in file_contents:
        if entry != "":
            info = entry.split(":")
            if info[0] not in current_maildirusers and "home" in info[5]:
                account_name = info[0]
                uid = info[2]
                gid = info[3]
                home_dir = info[5]
                account_info[account_name] = [uid, gid, home_dir]

    return account_info

def find_maildirs(mailbox_dirs):
    '''
    takes in dict containing account_name and home_dir, and checks for existence of either "mail" or "Maildir" directori
es
    within the home directory.
    '''
    users_to_convert = {}
    manual_int_req = {}
    for k,v in mailbox_dirs.items():
        box_path = "/var/mail/%s" % k
        home_mail_path = "%s/mail" % v[2]
        procmail_rc_path = "%s/.procmailrc" % v[2]
        if (os.path.exists(box_path) and get_file_size(box_path) != 0) or os.path.isdir(home_mail_path):
            if not os.path.exists(procmail_rc_path):
                users_to_convert[k] = v
            elif (os.path.exists(procmail_rc_path) and not (get_file_size(procmail_rc_path) == 34 or get_file_size(procm
ail_rc_path) == 35)):
                manual_int_req[k] = v
            else:
                users_to_convert[k] = v
    print "\n\nThere are", len(users_to_convert), "users who meet the following criteria:\n1. Are not in /etc/dovecot/ma
ildirusers\n2. Have a non-empty mailbox in /var/mail and\n3. Have a home directory\n4. Have a standard .procmailrc\n"
    print('-------------------------------------------------\n')
    print "The following %s users are going to be converted:\n" % len(users_to_convert)
    print('-------------------------------------------------')
    for k,v in users_to_convert.items():
        print(k)
    print('\n----------------------------------------------------------------------\n')
    print "The following %s users require manual intervention due to .procmailrc:\n" % len(manual_int_req)
    print('----------------------------------------------------------------------')
    for k,v in manual_int_req.items():
        print(k,v)

    return users_to_convert

def get_file_size(filename):
    '''
    function to check the size of files, which will take out mailboxes that are empty
    '''
    st = os.stat(filename)
    return st.st_size


def set_Maildir_perms(path, uid, gid):
    '''
    fuction to recursively set ownership on Maildir
    '''
    os.chown(path, uid, gid)
    for dirpath, dirnames, filenames in os.walk(path):
        for dname in dirnames:
            os.chown(os.path.join(dirpath, dname), uid, gid)
        for fname in filenames:
            os.chown(os.path.join(dirpath, fname), uid, gid)

def convert_mailboxes(users_to_convert):
    fail_safe = 0
    print('\n\n----------------------------------------------------------------\n')
    print('--------------------- Converting Mailboxes ---------------------\n')
    print('----------------------------------------------------------------\n')
    while True:
        confirm_conversion = raw_input("You are about to start converting mailboxes. The first 5 will be one at a time.
Please choose:\n1.) Continue\n9.) Quit\n> ")
        if confirm_conversion == "1":
             for k,v in users_to_convert.items():
                 print('\n----------------------------- %s ------------------------------\n' % k)
                 box_path = "/var/mail/%s" % k
                 home_mail_path = "%s/mail" % v[2]
                 home_Maildir_path = "%s/Maildir" % v[2]
                 procmail_path = "~%s" % v[2]
                 procmail_paths = [".procmailrc", ".procmailrc~", ".procmail-spamrc"]
                 # Convert /var/mail/ box, if exists
                 if os.path.exists(box_path):
                     subprocess.call("mb2md -s %s -d %s" % (box_path, home_Maildir_path), shell=True)
                     subprocess.call("mv %s %s.old" % (box_path, box_path), shell=True)
                 # Convert homedir IMAP folders, if exists
                 if os.path.isdir(home_mail_path):
                     subprocess.call("mb2md -s %s -d %s" % (home_mail_path, home_Maildir_path), shell=True)
                 # Sets permissions on ~$USER/Maildir
                 set_Maildir_perms(home_Maildir_path, int(v[0]), int(v[1]))
                 # Copy .procmail* to homedir
                 subprocess.call("cp /home/jonathanweaver/tmp/procfiles/.procmail* %s/" % v[2], shell=True)
                 # Set permissions on .procmailrc* files
                 for procmail_file in procmail_paths:
                     subprocess.call("chown %s:%s %s/%s" % (int(v[0]), int(v[1]), v[2], procmail_file), shell=True)
                 with open('/etc/dovecot/maildirusers', 'a') as f:
                     f.write(k + "\n")

                 if fail_safe < 5:
                     fail_safe += 1
                     x = raw_input("Press any button to continue...")


             subprocess.call("/etc/dovecot/passwd-gen.pl", shell=True)
             subprocess.call("cat /etc/dovecot/passwd.tmp > /etc/dovecot/passwd", shell=True)
             break

        elif confirm_conversion == "9":
             print("Goodbye!\n")
             break

        else:
             print("\n\nYou must make a valid selection, please try again!\n\n")

# Gets list of current Maildir users, aka users we can skip
current_maildirusers = get_current_maildirusers()
# Gets list of all users in /etc/passwd and then removes users already in /etc/dovecot/maildirusers or that are service
accounts and thus has no homedir
mailbox_dirs = get_non_maildirusers(current_maildirusers)
#pprint(mailbox_dirs)
# Weeds out users that have a box in /var/mail/ that is nonexistent and/or empty and returns final list of users to conv
ert mboxes for
users_to_convert = find_maildirs(mailbox_dirs)
x = raw_input("\nPress any button to continue...")
# Converts mailboxes in user list
if users_to_convert:
    convert_mailboxes(users_to_convert)
else:
    print("There are no mailboxes left to auto-migrate to Maildir format!\n\nGoodbye!")
