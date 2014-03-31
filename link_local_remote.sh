#! /bin/bash
OLD_DIR=`pwd`
LOCAL_CONFIG=$OLD_DIR/conf/local.config.yaml

SSH_ROOT=$1
LOCAL_REMOTE_FOLDER=$2
LOCAL_REMOTE_PWD=$3
REMOTE_HOST=$4
REMOTE_PORT=$5

# ssh into annex to establish trust (AKA ToFUPoP)
ssh -t -oStrictHostKeyChecking=no -i $SSH_ROOT/unveillance.local_remote.key root@$REMOTE_HOST -p $REMOTE_PORT -v 'sudo echo "$LOCAL_REMOTE_PWD"'

# append to ssh/config
echo unveillance.local_remote.port: $REMOTE_PORT >> $LOCAL_CONFIG
# Host $REMOTE_HOST
#	IdentityFile $SSH_ROOT/unveillance.local_remote.key
#	Port $REMOTE_PORT

git clone ssh://root@$REMOTE_HOST/home/unveillance_remote $LOCAL_REMOTE_FOLDER
cd $LOCAL_REMOTE_FOLDER
mkdir .synctasks
echo .DS_Store > .gitignore
echo *.pyc >> .gitignore
echo *.exe >> .gitignore
echo .synctasks/local/ >> .gitignore

git annex init "unveillance_remote"
git annex untrust web
git remote add unveillance_remote ssh://root@$REMOTE_HOST/home/unveillance_remote

cd $OLD_DIR
echo True