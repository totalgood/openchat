# https://unix.stackexchange.com/questions/322883/how-to-correctly-set-hostname-and-domain-name#322886
DOMAIN_NAME=totalgood.org
BASHRC_PATH="$HOME/.bashrc"

if [[ -f "$BASHRC_PATH" ]] ; then
	BASHRC_PATH="$BASHRC_PATH"
else
	# for darwin/mac
	BASHRC_PATH="$HOME/.bash_profile"
fi

sed 's/HISTCONTROL=[a-z]*/HISTCONTROL=""/g' -i "$BASHRC_PATH"
sed 's/HISTSIZE=[0-9]*/HISTSIZE=1000000/g' -i "$BASHRC_PATH"
sed 's/HISTFILESIZE=[0-9]*/HISTFILESIZE=2000000/g' -i "$BASHRC_PATH"
sed "s/alias hist='history | cut -c8-'/\1/g" -i "$HOME/.bash_aliases" || echo "alias hist='history | cut -c8-'" >> "$HOME/.bash_aliases"
source "$BASHRC_PATH"

sudo echo 'big-openchat' | sudo tee '/etc/hostname'
sudo hostname $(cat /etc/hostname)
grep "domain $DOMAIN_NAME" /etc/resolv.conf || sudo echo "domain $DOMAIN_NAME" | sudo tee --append /etc/resolv.conf

# Create security group with Inbound rules that allow:
#     22 80 443 8000 ICMP-echo-request ICMP-echo-reply ICMP-domainname-reply ICMP-traceroute-reply
# Assign that security group to you EC2 isntances

# Add elastic IP to EC2 instance
# Add A-record to Route 53 DNS table with empty subdomain and public IP address
# Add CNAME-record to Route 53 with www subdomain and target same as A-record