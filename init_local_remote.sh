#! /bin/bash
SSH_ROOT=$1
LM=$2
LOCAL_REMOTE_PWD=$3
CONF_ROOT=$4
REMOTE_HOST=$5
REMOTE_PORT=$6
REMOTE_USER=$7
REMOTE_PATH=$8

LOCAL_REMOTE_PARENT=`dirname "$LM"`
LOCAL_REMOTE_FOLDER=`basename "$LM"`
LOCAL_CONFIG=$CONF_ROOT/conf/local.config.yaml

# if it exists...
has_lm=$(find $LOCAL_REMOTE_PARENT -type d -name "$(echo $LOCAL_REMOTE_FOLDER)")
if [[ -z "$has_lm" ]]
then
	echo "checking dir"
else
	echo "dir exists. must be blank!"
	# return error here pls.
fi

NEW_SSH_KEY=$SSH_ROOT/unveillance.$(`date +%s`).key
ssh-keygen -f $NEW_SSH_KEY -t rsa -b 4096 -N $LOCAL_REMOTE_PWD

echo unveillance.local_remote.folder: $LM >> $LOCAL_CONFIG
echo unveillance.local_remote.port: $REMOTE_PORT >> $LOCAL_CONFIG
echo unveillance.local_remote.hostname: $REMOTE_HOST >> $LOCAL_CONFIG
echo unveillance.local_remote.user: $REMOTE_USER >> $LOCAL_CONFIG
echo unveillance.local_remote.remote_path: $REMOTE_PATH >> $LOCAL_CONFIG
echo unveillance.local_remote.pub_key: $NEW_SSH_KEY.pub >> $LOCAL_CONFIG

echo "Host $REMOTE_HOST" >> $SSH_ROOT/config
echo "	IdentityFile $NEW_SSH_KEY" >> $SSH_ROOT/config
if [ $REMOTE_PORT -eq 22 ]
then
	echo "	Port $REMOTE_PORT" >> $SSH_ROOT/config
fi