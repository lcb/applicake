#!/bin/bash


grep '=' src/applicake/framework/enums.py | awk '{print $1}' | while read key
do
	echo $key
	sed -i "" "s/self\.$key/Keys\.$key/g" $(find . -name '*.py')
done

sed -i "8 i from applicake.framework.keys import Keys" $(find src/applicake/ -name '*.py')
