# gcov

Compile your code along with the embedded-gcov and the code from nasa [(https://github.com/nasa-jpl/embedded-gc…)](https://github.com/nasa-jpl/embedded-gcov) the following compiler flags ( -fprofile-arcs -ftest-coverage ). add a call to _gcov_exit() at the end of your application. [The call to _gcov_exit() is not really required if its a dkm, as dkm unload automatically calls this method]

There are a couple of options there to output the coverage gcda over serial output, binary file etc... please feel free to read the nasa readme for more info. The one I prefer is to use the binary file and store it in the hostfs and wrote my own parser to separate single binary file into multiple *.gcda files, which is quite easy with python. Scripts to parse the blob to multiple gcda files can be found in scripts/gcda_splitter.py

I'd suggest to use the serial output as they have all the scripts in place to convert the console output to multiple *.gcda files.

I did not see any lcov with the toolchain that vxworks provided, I used a lcov from a different installation, in that case you might have to point lcov to the gcov tool that was used in my case.

$ lcov --gcov-tool /home/user/WindRiver/compilers/gnu-8.3.0.2/x86_64-linux2/bin/gcovppcspe --capture --directory . --output-file coverage.info

finally run genhtml with the coverage.info to get the html report.
