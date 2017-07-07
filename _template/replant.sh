#!/bin/bash

[ -z "$1" ] && exit 1

for eid in $(cat __clusterdir/nodes.lst) ; do
  ./replant.sh $eid-$1
done
