#!/bin/bash
firstnode=yes
for eid in $(cat __clusterdir/nodes.lst) ; do
  echo $eid : 
  if [ $firstnode == yes ] ; then
    echo $(echo "$@" | python _plugin/spider/_script/create_table_filter.py 0 __clusterdir/nodes.lst | cat)
    firstnode=no
  else
    echo $(echo "$@" | python _plugin/spider/_script/create_table_filter.py | cat)
  fi
done
