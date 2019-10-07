Requires Python 2.x


Procedure for migration:

•	shut down mail, sendmail and dovecot on mail.poweruser.com before the rsync OR set up iptable rules to 1. log incoming packets and then 2. drop traffic:

		iptables -I INPUT -m state --state NEW -m tcp -p tcp --match multiport --dports 25,26,465,587,143,993,110,995 -j DROP

		iptables -I INPUT -m state --state NEW -m tcp -p tcp --match multiport --dports 25,26,465,587,143,993,110,995 -j LOG --log-prefix '[IPTABLES INPUT MAIL] reject'

		# iptables -vnL --line-numbers

		# iptables -D INPUT 1

•	rsync mail

•	swap PUI DNS records to point at cp7

•	fix proofpoint IP addresses

•	rsync mail again to ensure stragglers make it over

•	Run cPanel AutoSSL to obtain certs

•	Update maildir size (via cli)

		/scripts/generate_maildirsize --confirm --allaccounts --verbose poweruser

•	Fix mail permissions (via WHM)

•	Remove shell access for Poweruser account (enabled presently for rsync)
