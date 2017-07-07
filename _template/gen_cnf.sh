#!/bin/bash
for eid in $(cat __clusterdir/nodes.lst) ; do
  echo -n $eid : 
  echo $($eid*/gen_cnf.sh "$@") 
done
