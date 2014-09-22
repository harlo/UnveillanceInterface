#! /bin/bash
if [ $# -eq 0 ]
then
	TARG=frontend
else
	TARG=$1
fi

tail -f .monitor/$TARG.log.txt