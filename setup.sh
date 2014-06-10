#! /bin/bash
THIS_DIR=`pwd`
LOCAL_CONFIG=$THIS_DIR/conf/local.config.yaml

if [ $# -eq 0 ]
then
	echo "no initial arguments (Stock Unveillance context)"
	OLD_DIR=$THIS_DIR
	LAUNCH_FRONTEND=true
	SSH_ROOT=~/.ssh
	SERVER_HOST="10.51.118.238"
	SERVER_PORT=8888
	SERVER_USE_SSL=false
else
	OLD_DIR=$1
	LAUNCH_FRONTEND=false
	SSH_ROOT=$2
	SERVER_HOST=$3
	SERVER_PORT=$4
	SERVER_USE_SSL=$5
fi

mkdir $THIS_DIR/.monitor
mkdir $THIS_DIR/tmp

echo ssh_root: $(dirname $SSH_ROOT)/$(basename $SSH_ROOT) > $LOCAL_CONFIG
echo server.host: $SERVER_HOST >> $LOCAL_CONFIG
echo server.port: $SERVER_PORT >> $LOCAL_CONFIG
echo server.use_ssl: $SERVER_USE_SSL >> $LOCAL_CONFIG

cd $THIS_DIR/lib/Core
pip install --upgrade -r requirements.txt

cd $THIS_DIR
pip install --upgrade -r requirements.txt

GENERATE_COOKIE_SECRET="from lib.Core.Utils.funcs import generateSecureNonce;print generateSecureNonce()"
echo api.web.cookie_secret: $(python -c "$GENERATE_COOKIE_SECRET") >> $LOCAL_CONFIG

cd $OLD_DIR

if $LAUNCH_FRONTEND
then
	echo "**************************************************"
	echo "Launching frontend..."
	python unveillance_frontend.py -firstuse
fi