#download mongo
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list


sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-pip
sudo apt-get install python-dev
sudo apt-get install build-essential
sudo apt-get install python-virtualenv
sudo apt-get install -y mongodb-org
#start mongo
#sudo service mongod start

virtualenv flask

flask/bin/pip install flask
flask/bin/pip install flask-httpauth
flask/bin/pip install flask-restful
flask/bin/pip install gunicorn
flask/bin/pip install pymongo
flask/bin/pip install tornado
