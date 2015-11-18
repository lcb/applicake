[![Build Status](https://travis-ci.org/lcb/applicake.svg)](https://travis-ci.org/lcb/applicake)
[![Project Stats](https://www.openhub.net/p/applicake/widgets/project_thin_badge.gif)](https://www.openhub.net/p/applicake)

How to setup applicake
======================

Go to the folder where you want to install applicake
$ cd /install_dir/

make applicake available to your python environment by adding the root folder to your pytonpath
$ vim ~/.bashrc
export PYTHONPATH=/install_dir/applicake-master/applicake/:/install_dir/applicake-master/appliapps/:$PYTHONPATH

for testing sucessful install try
$ /install_dir/applicake-master/executables/ruffus/echoWF.py

for testing sucessful install try
python.exe .\appliapps\examples\cp.py --FILE "test"
