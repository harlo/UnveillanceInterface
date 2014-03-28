#! /bin/bash
OLD_DIR=`pwd`
LOCAL_CONFIG=$OLD_DIR/conf/local.config.yaml

SSH_ROOT=$1
LOCAL_REMOTE_FOLDER=$2
LOCAL_REMOTE_PWD=$3
REMOTE_HOST=$4
REMOTE_PORT=$5

echo unveillance.local_remote.port: $REMOTE_PORT >> $LOCAL_CONFIG