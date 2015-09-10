#!/bin/bash
# mkdoc.sh: makes epydoc


EXCLUDES="CMakeLists.*|__init__.*|build_utils_codes.*|qa_*" #build_utils.*"
if [ ! "$1" ]
then
  PRJNM=GR-GWN
  ##echo "Usage: mkdoc.sh <project name>"
else
  PRJNM="$1"
fi

if [ -d "html" ]
then
  rm -r html/*
else 
  mkdir html
fi

CURDIR=`pwd`          # the current directory
CODEDIR='../python'   # directory where python code is placed
HTMLDIR=$CURDIR       # directory where HTML docs are to be placed
#echo $CURDIR
#echo epydoc -v --name $PRJNM -o ${CURDIR}/html --exclude "$EXCLUDES" .
cd ../python
epydoc -v --name $PRJNM -o ${HTMLDIR}/html --exclude "$EXCLUDES" . #$CODEDIR
cd $CURDIR

