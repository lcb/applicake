How to install applicake
========================

Go to the folder where you want to install applicake

cd /install_dir/

Download latest stable version: svn co http://applicake.googlecode.com/svn/tags/?.?.? applicake-?.?.?
*or*
Download latest development version: svn co http://applicake.googlecode.com/svn/trunk/ applicake-trunk

make applicake available to your python environment by adding the root folder to your pytonpath

$ vim ~/.bashrc
export PYTHONPATH=/install_dir/applicake/:$PYTHONPATH

for testing sucessful install try
$ ./executables/ruffus/echoWF.py