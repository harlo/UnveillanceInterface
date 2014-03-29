#! /bin/bash
$SERVER_NAME=$1
OLD_DIR=`pwd`
LOCAL_CONFIG=$OLD_DIR/conf/local.config.yaml

echo "**************************************************"
echo "************** ANNEX SETUP **************"
mkdir $OLD_DIR/.monitor

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
	SERVER_USE_SSL=8888
fi
echo server.port: $SERVER_USE_SSL >> $LOCAL_CONFIG

sudo pip install --upgrade -r requirements.txt