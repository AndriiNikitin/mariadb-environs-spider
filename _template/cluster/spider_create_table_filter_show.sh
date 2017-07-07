#!/bin/bash
for eid in $(cat __clusterdir/nodes.lst) ; do
  echo $eid : 
  echo $(echo "$@" | python _plugin/spider/create_table_filter.py "$([[ $eid =~ 0 ]] && echo 0)" | cat)
done
