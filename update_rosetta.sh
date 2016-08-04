curl -OL https://raw.github.com/RosettaCommons/rosetta_clone_tools/master/get_rosetta.sh
bash get_rosetta.sh
cd Rosetta/main/source/
./scons.py -j10 cxx=clang mode=release bin
