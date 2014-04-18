#! /bin/bash
OLD_DIR=`pwd`
LOCAL_CONFIG=$OLD_DIR/conf/local.config.yaml

SSH_ROOT=$1
LOCAL_REMOTE_FOLDER=$2
REMOTE_HOST=$3
REMOTE_PORT=$4
REMOTE_USER=$5
REMOTE_PATH=$6

# ssh into annex to establish trust (AKA ToFUPoP)
ssh -t -oStrictHostKeyChecking=no -i $SSH_ROOT/unveillance.local_remote.key $REMOTE_USER@$REMOTE_HOST -p $REMOTE_PORT -v <<EOF
echo "hello" > /dev/null 2>&1
EOF

# append to ssh/config
echo unveillance.local_remote.port: $REMOTE_PORT >> $LOCAL_CONFIG
echo "Host $REMOTE_HOST" >> $SSH_ROOT/config
echo "	IdentityFile $SSH_ROOT/unveillance.local_remote.key" >> $SSH_ROOT/config
echo "	Port $REMOTE_PORT" >> $SSH_ROOT/config

git clone ssh://$REMOTE_USER@$REMOTE_HOST$REMOTE_PATH $LOCAL_REMOTE_FOLDER
cd $LOCAL_REMOTE_FOLDER
mkdir .synctasks
echo .DS_Store > .gitignore
echo *.pyc >> .gitignore
echo *.exe >> .gitignore
echo .synctasks/local/ >> .gitignore

git annex init "unveillance_remote"
git annex untrust web
git remote add unveillance_remote ssh://$REMOTE_USER@$REMOTE_HOST$REMOTE_PATH

cd $OLD_DIR
echo True