#! /bin/bash
THIS_DIR=`pwd`
if [ $# -eq 0 ]
then
	UV_MASTER=$THIS_DIR/unveillance_frontend.py
	LAUNCH_FRONTEND=true
else
	UV_MASTER=$1
	LAUNCH_FRONTEND=false
fi

./shutdown.sh $UV_MASTER
python reset.py

sudo rm $THIS_DIR/conf/local.config.yaml

cat $THIS_DIR/conf/unveillance.secrets.json > $THIS_DIR/conf/unveillance.secrets.json.backup
sudo rm $THIS_DIR/conf/unveillance.secrets.json
mv $THIS_DIR/conf/unveillance.secrets.json.backup $THIS_DIR/conf/unveillance.secrets.json

./setup.sh $THIS_DIR/conf/unveillance.secrets.json

if $LAUNCH_FRONTEND; then
	chmod 0400 conf/unveillance.secrets.json
	python unveillance_frontend.py -firstuse
fi