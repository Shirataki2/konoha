#!/bin/bash
cmd="docker-compose -f docker-compose.$1.yml -p $1 ${@:2}"
echo $cmd
eval $cmd