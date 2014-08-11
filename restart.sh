THIS_DIR=`pwd`
if [ $# -eq 0 ]
then
	UV_MASTER=$THIS_DIR/unveillance_frontend.py
else
	UV_MASTER=$1
fi

./shutdown.sh $UV_MASTER
sleep 5
./startup.sh $UV_MASTER