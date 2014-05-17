#! /bin/bash
OLD_DIR=`pwd`

LOCAL_REMOTE_FOLDER=$1
REMOTE_HOST=$2
REMOTE_USER=$3
REMOTE_PATH=$4

# ssh into annex to establish trust (AKA ToFUPoP)
ssh -t -oStrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST -v <<EOF
echo "hello" > /dev/null 2>&1
EOF

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