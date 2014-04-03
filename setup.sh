#! /bin/bash
THIS_DIR=`pwd`
LOCAL_CONFIG=$THIS_DIR/conf/local.config.yaml

if [ $# -eq 0 ]
then
	echo "no initial arguments (Stock Unveillance context)"
	OLD_DIR=$THIS_DIR
	FRONTEND_NAME=unveillance_frontend
else
	OLD_DIR=$1
	FRONTEND_NAME=$2
fi

echo "**************************************************"
echo "************** FRONTEND SETUP **************"
mkdir $OLD_DIR/.monitor
mkdir $OLD_DIR/tmp

echo "What's the full path to your ssh folder? (i.e ~/.ssh)"
echo "[DEFAULT: ~/.ssh]: "
read SSH_ROOT
if [[ -z "$SSH_ROOT" ]]
then
	SSH_ROOT=~/.ssh
fi
echo ssh_root: $(dirname $SSH_ROOT)/$(basename $SSH_ROOT) > $LOCAL_CONFIG

echo "Enter your Server's IP address (i.e. 192.168.1.101)"
echo ": "
read SERVER_HOST
echo server.host: $SERVER_HOST >> $LOCAL_CONFIG

echo "Enter your Server's port (i.e. 8888)"
echo "[DEFAULT: 8888]:"
read SERVER_PORT
if [[ -z "$SERVER_PORT" ]]
then
	SERVER_PORT=8888
fi
echo server.port: $SERVER_PORT >> $LOCAL_CONFIG

echo "Your Server support SSL connections: true or false?"
echo "[DEFAULT: false]:"
read SERVER_USE_SSL
if [[ -z "$SERVER_USE_SSL" ]]
then
	SERVER_USE_SSL=false
fi
echo server.use_ssl: $SERVER_USE_SSL >> $LOCAL_CONFIG

sudo pip install --upgrade -r requirements.txt

echo "**************************************************"
echo "Launching frontend..."
cd $OLD_DIR
python $FRONTEND_NAME.py -firstuse