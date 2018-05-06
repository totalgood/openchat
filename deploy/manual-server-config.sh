# https://unix.stackexchange.com/questions/322883/how-to-correctly-set-hostname-and-domain-name#322886
GH_ORG='totalgood'
GH_PRJ='openchat'
APPNAME='openspaces'
DBNAME='hackor'
DBUN=postgres
RED='\033[0;31m'
NC='\033[0m' # no color
if [[ -n $DBPW || -z "$DBPW" ]] ; then
    DBPW='\\ChangeMe\!\!\! '
    printf "$RED WARNING: Don't forget to update your admin user info for Zak and Hobs !!!!!!!$NC\\n"
    printf "$RED DBPW=$DBPW$NC\\n"
fi
DOMAIN_NAME='totalgood.org'
SUBDOMAIN_NAME="GH_PRJ"
BASHRC_PATH="$HOME/.bashrc"
PUBLIC_IP='34.211.189.63'  # from AWS EC2 Dashboard
SRV='/srv'
VIRTUALENVS="$SRV/virtualenvs"
SRV_MANAGEPY="$SRV/$GH_PRJ" 
export DOCKER_DEV=true  # DOCKER_DEV=false uses postgis instead of postgresql backend in settings.py

if [[ -f "$BASHRC_PATH" ]] ; then
    BASHRC_PATH="$BASHRC_PATH"
else
    # for darwin/mac
    BASHRC_PATH="$HOME/.bash_profile"
fi



###### ON MAC LAPTOP !!!!!!!! #######

sudo echo "$PUBLIC_IP $DOMAIN_NAME" | sudo tee --append /etc/hosts
sudo echo "$PUBLIC_IP www.$DOMAIN_NAME" | sudo tee --append /etc/hosts
sudo echo "$PUBLIC_IP $SUBDOMAIN_NAME.$DOMAIN_NAME" | sudo tee --append /etc/hosts

ssh $SUBDOMAIN_NAME

# add domain and pem file path to .ssh/config
#####################################



####### on remote AWS EC2 instance #######

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
#     See: https://stackoverflow.com/a/30544572/623735
# Assign that security group to you EC2 isntances

# Add elastic IP to EC2 instance
# Add A-record to Route 53 DNS table with empty subdomain and public IP address
# Add CNAME-record to Route 53 with www subdomain and target same as A-record

sudo mkdir -p "$SRV"
sudo chown $USER "$SRV"
mkdir -p "$VIRTUALENVS"
ln -s "$VIRTUALENVS" "$HOME/.virtualenvs"
cd "$SRV"
python3 -m venv "$VIRTUALENVS/${GH_PRJ}_venv"
source "$VIRTUALENVS/${GH_PRJ}_venv/bin/activate"
pip install --upgrade pip wheel

git clone "https://github.com/${GH_ORG}/${GH_PRJ}.git" "$SRV/$GH_PRJ"
pip install -r "$SRV_MANAGEPY/requirements.txt"

###################################################




###### ON MAC LAPTOP !!!!!!!! #######

scp ~/src/openchat/openchat/local_settings.py $GH_PRJ:/srv/$GH_PRJ/$GH_PRJ/

#####################################



####### on remote AWS EC2 instance #######

source "$VIRTUALENVS/${GH_PRJ}_venv/bin/activate"
sudo timedatectl set-timezone UTC
sudo locale-gen en_US
sudo locale-gen en_US.UTF-8
sudo update-locale en_US.UTF-8

sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main"
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt install -y nginx postgresql postgresql-contrib python3-psycopg2 ntp wget git nano 
pip install --upgrade psycopg2 --no-cache-dir
sudo sed -i -r 's/port[ ][=][ ]54[0-9][0-9]/port = 5432/g' /etc/postgresql/*/main/postgresql.conf
# sudo apt remove -y postgresql-9.6
sudo service postgresql restart


sudo -u postgres createdb --encoding='UTF-8' --lc-collate='en_US.UTF-8' --lc-ctype='en_US.UTF-8' --template='template0' $DBNAME "For openchat hackor and other totalgood.org projects"
sudo -u postgres echo "ALTER USER $DBUN WITH PASSWORD '$DBPW';" | sudo -u postgres psql $DBNAME

# WIPE THE DATABASE !!!!!
rm -rf $SRV_MANAGEPY/$APPNAME/migrations
mkdir -p $SRV_MANAGEPY/$APPNAME/migrations
touch -p $SRV_MANAGEPY/$APPNAME/migrations/__init__.py  # ensures that migrations are created/run for this app
rm -f db.sqlite3
source "$VIRTUALENVS/${GH_PRJ}_venv/bin/activate"
python manage.py makemigrations
python manage.py makemigrations openspaces  # this should have already happened if everything went well above
python manage.py migrate
python manage.py collectstatic
echo "from django.contrib.auth.models import User" > createadmin.py
echo "User.objects.create_superuser('hobs', 'hobs+$APPNAME@totalgood.com', 'hobs$DBPW')" >> createadmin.py
echo "User.objects.create_superuser('zak', 'zak.kent+$APPNAME@gmail.com', 'zak$DBPW')" >> createadmin.py
python manage.py shell < createadmin.py
rm createadmin.py

# https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-16-04
sudo rm /etc/nginx/sites-available/totalgood.org.conf
sudo rm /etc/nginx/sites-enabled/totalgood.org.conf
sudo cp deploy/nginx/simple.totalgood.org.conf /etc/nginx/sites-enabled/totalgood.org.conf
sudo rm /etc/nginx/sites-enabled/default
sudo ln etc/nginx/sites-enabled/totalgood.org.conf /etc/nginx/sites-available/totalgood.org.conf
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get install -y python-certbot-nginx
sudo certbot -n --agree-tos -m admin@totalgood.com --nginx -d totalgood.org,www.totalgood.org # -d pycon.totalgood.org -d openchat.totalgood.org -d big-openchat.totalgood.org -d big.openchat.totalgood.org -d openspaces.totalgood.org

cd /srv/logs/
mkdir -p letsencrypt
cd letsencrypt
wget 'https://www.ssllabs.com/ssltest/analyze.html?d=totalgood.org&latest' -O ssllabs_analyze_totalgood.org.html
sudo certbot renew --dry-run

###################################################


##############################################################################
## webroot certonly letsencrypt session

## second attempt
sudo certbot -m admin@totalgood.com certonly --webroot -d www.totalgood.org -d totalgood.org
# Saving debug log to /var/log/letsencrypt/letsencrypt.log
# Plugins selected: Authenticator webroot, Installer None
# Cert not yet due for renewal

# You have an existing certificate that has exactly the same domains or certificate name you requested and isn't close to expiry.
# (ref: /etc/letsencrypt/renewal/totalgood.org.conf)

# What would you like to do?
# -------------------------------------------------------------------------------
# 1: Keep the existing certificate for now
# 2: Renew & replace the cert (limit ~5 per 7 days)
# -------------------------------------------------------------------------------
# Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
# Renewing an existing certificate
# Performing the following challenges:
# http-01 challenge for www.totalgood.org
# http-01 challenge for totalgood.org
# Input the webroot for www.totalgood.org: (Enter 'c' to cancel): /srv/openchat/collected

# Select the webroot for totalgood.org:
# -------------------------------------------------------------------------------
# 1: Enter a new webroot
# 2: /srv/openchat/collected
# -------------------------------------------------------------------------------
# Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
# Waiting for verification...
# Cleaning up challenges

# IMPORTANT NOTES:
#  - Congratulations! Your certificate and chain have been saved at:
#    /etc/letsencrypt/live/totalgood.org/fullchain.pem
#    Your key file has been saved at:
#    /etc/letsencrypt/live/totalgood.org/privkey.pem
#    Your cert will expire on 2018-08-03. To obtain a new or tweaked
#    version of this certificate in the future, simply run certbot
#    again. To non-interactively renew *all* of your certificates, run
#    "certbot renew"
#  - If you like Certbot, please consider supporting our work by:

#    Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
#    Donating to EFF:                    https://eff.org/donate-le


sudo certbot -m admin@totalgood.com certonly --webroot -d totalgood.org
# Saving debug log to /var/log/letsencrypt/letsencrypt.log
# Plugins selected: Authenticator webroot, Installer None
# Obtaining a new certificate
# Performing the following challenges:
# http-01 challenge for totalgood.org
# http-01 challenge for www.totalgood.org
# Input the webroot for totalgood.org: (Enter 'c' to cancel): /srv/openchat/collected

# Select the webroot for www.totalgood.org:
# -------------------------------------------------------------------------------
# 1: Enter a new webroot
# 2: /srv/openchat/collected
# -------------------------------------------------------------------------------
# Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
# Waiting for verification...
# Cleaning up challenges

# IMPORTANT NOTES:
#  - Congratulations! Your certificate and chain have been saved at:
#    /etc/letsencrypt/live/totalgood.org/fullchain.pem
#    Your key file has been saved at:
#    /etc/letsencrypt/live/totalgood.org/privkey.pem
#    Your cert will expire on 2018-08-03. To obtain a new or tweaked
#    version of this certificate in the future, simply run certbot
#    again. To non-interactively renew *all* of your certificates, run
#    "certbot renew"
#  - If you like Certbot, please consider supporting our work by:

#    Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
#    Donating to EFF:                    https://eff.org/donate-le


###############################################################################