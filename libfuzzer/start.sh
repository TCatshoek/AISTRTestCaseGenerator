#!/bin/bash

PROBLEMSET_NAME=$1
TMUX_NAME=libfuzzer_$1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

tmux new-session -d -s $TMUX_NAME

att() {
        [ -n "${TMUX:-}" ] &&
        tmux switch-client -t "=${TMUX_NAME}" ||
        tmux attach-session -t "=${TMUX_NAME}"
}


cd $DIR/$PROBLEMSET_NAME

for d in */
do
        tmux new-window -d -t "=${TMUX_NAME}" -n ${d%/} -c $DIR/$PROBLEMSET_NAME/$d
        tmux send-keys -t "=${TMUX_NAME}:=${d%/}" "./${d%/}_fuzz corpus -dict=./dict" Enter
done

att
