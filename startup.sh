THIS_DIR=`pwd`
if [ $# -eq 0 ]
then
	UV_MASTER=$THIS_DIR
else
	UV_MASTER=$1
fi

python $UV_MASTER -start