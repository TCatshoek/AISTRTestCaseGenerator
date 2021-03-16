# AISTRTestCaseGenerator
Script to generate testcases for the third assignment of the 2020 AISTR course. Probably only runs on Linux. 

It uses libFuzzer to fuzz the RERS problems, generating inputs that maximize the coverage through the problems.

Make sure the following is available on your system:
```
clang
gcc
tmux
unzip
wget
python (> 3.6)
```

### To run:
- First download, patch and compile the RERS 2020 problems with the provided `prepare_*.sh` scripts in the `libfuzzer` directory
- Then use the provided start script `start.sh` to start fuzzing: 
```
cd libfuzzer
./start.sh SeqReachabilityRers2020
./start.sh SeqLtlRers2020
```
- Once you feel you have fuzzed long enough, kill the tmux sessions `tmux kill-session -t *session name*` and run `main.py`
- Output will appear in `testcases`