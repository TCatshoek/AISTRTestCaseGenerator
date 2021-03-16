### LibFuzzer scripts

To download and compile the rers problems you want, run the corresponding shell script, e.g. `./prepare_ltl_2020.sh`
Besides python, the scripts require clang, tmux, unzip, and wget to be available on your system.

Then, to start fuzzing, run `./start.sh <problemsetname>` e.g. `./start.sh SeqLtlRers2020`

This will spawn a tmux session with a window running the fuzzer for each problem and attach to it.