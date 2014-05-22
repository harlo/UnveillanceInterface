#! /bin/bash
LM=$1
LOCAL_REMOTE_PWD=$2
REMOTE_HOST=$3
REMOTE_PORT=$4
REMOTE_USER=$5
REMOTE_PATH=$6
UV_UUID=$7
SSH_ROOT=$8
CONF_ROOT=$9

LOCAL_REMOTE_PARENT=`dirname "$LM"`
LOCAL_REMOTE_FOLDER=`basename "$LM"`
LOCAL_CONFIG=$CONF_ROOT/local.config.yaml

# if it exists...
has_lm=$(find $LOCAL_REMOTE_PARENT -type d -name "$(echo $LOCAL_REMOTE_FOLDER)")
if [[ -z "$has_lm" ]]
then :
else
	echo "False"
fi

SECS=`date +%s`
NEW_SSH_KEY=$SSH_ROOT/unveillance.$SECS.key
ssh-keygen -f $NEW_SSH_KEY -t rsa -b 4096 -N $LOCAL_REMOTE_PWD

echo unveillance.local_remote.folder: $LM >> $LOCAL_CONFIG
echo unveillance.local_remote.port: $REMOTE_PORT >> $LOCAL_CONFIG
echo unveillance.local_remote.hostname: $REMOTE_HOST >> $LOCAL_CONFIG
echo unveillance.local_remote.user: $REMOTE_USER >> $LOCAL_CONFIG
echo unveillance.local_remote.remote_path: $REMOTE_PATH >> $LOCAL_CONFIG
echo unveillance.local_remote.pub_key: $NEW_SSH_KEY >> $LOCAL_CONFIG
echo unveillance.uv_uuid: $UV_UUID

echo "Host $REMOTE_HOST" >> $SSH_ROOT/config
echo "	IdentityFile $NEW_SSH_KEY" >> $SSH_ROOT/config
if [ $REMOTE_PORT -eq 22 ]
then :
else
	echo "	Port $REMOTE_PORT" >> $SSH_ROOT/config
fi

echo "True"