apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
apt-get -qqy install python-appdirs
apt-get -qqy install python-blinker
apt-get -qqy install python-click
apt-get -qqy install python-Flask
apt-get -qqy install python-Flask-Admin
apt-get -qqy install python-Flask-DebugToolbar
apt-get -qqy install python-Flask-SQLAlchemy
apt-get -qqy install python-itsdangerous
apt-get -qqy install python-Jinja2
apt-get -qqy install python-MarkupSafe
apt-get -qqy install python-packaging
apt-get -qqy install python-pyparsing
apt-get -qqy install python-six
apt-get -qqy install python-SQLAlchemy
apt-get -qqy install python-Werkzeug
apt-get -qqy install python-WTForms
pip install bleach
pip install oauth2client
pip install requests
pip install httplib2
pip install redis
pip install passlib
pip install itsdangerous
pip install flask-httpauth
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'
su vagrant -c 'createdb forum'
su vagrant -c 'psql forum -f /vagrant/forum/forum.sql'

vagrantTip="[35m[1mThe shared directory is located at /vagrant\nTo access your shared files: cd /vagrant(B[m"
echo -e $vagrantTip > /etc/motd

wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
make install