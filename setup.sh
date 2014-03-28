#! /bin/bash
$SERVER_NAME=$1
OLD_DIR=`pwd`
LOCAL_CONFIG=$OLD_DIR/conf/local.config.yaml

echo "**************************************************"
echo "************** ANNEX SETUP **************"
mkdir $OLD_DIR/.monitor

echo "What's the full path to your ssh folder?"
echo "(usually, ~/.ssh)"
read SSH_HOME
echo ssh_root: $SSH_HOME > $LOCAL_CONFIG

echo "Enter your Server's IP address:"
read SERVER_HOST
echo server_host: $SERVER_HOST > $LOCAL_CONFIG

sudo pip install --upgrade -r requirements.txt