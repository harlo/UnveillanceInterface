#! /bin/bash
OLD_DIR=`pwd`
LOCAL_CONFIG=$OLD_DIR/conf/local.config.yaml

SSH_ROOT=$1

LM=$2
LOCAL_REMOTE_PARENT=`dirname "$LM"`
LOCAL_REMOTE_FOLDER=`basename "$LM"`
LOCAL_REMOTE_PWD=$3

# if it exists...
has_lm=$(find $LOCAL_REMOTE_PARENT -type d -name "$(echo $LOCAL_REMOTE_FOLDER)")
if [[ -z "$has_lm" ]]
then
	echo "checking dir"
else
	echo "dir exists. must be blank!"
	# return error here pls.
fi

ssh-keygen -f $SSH_ROOT/unveillance.local_remote.key -t rsa -b 4096 -N $LOCAL_REMOTE_PWD

echo unveillance.local_remote.folder: $LM >> $LOCAL_CONFIG
echo unveillance.local_remote.password: $LOCAL_REMOTE_PWD >> $LOCAL_CONFIG