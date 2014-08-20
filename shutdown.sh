#! /bin/bash
THIS_DIR=`pwd`
if [ $# -eq 0 ]
then
	UV_MASTER=$THIS_DIR/unveillance_frontend.py
else
	UV_MASTER=$1
fi

python $UV_MASTER -stop
python shutdown.py $UV_MASTER