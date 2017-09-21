#!/bin/bash
firstnode=yes
for eid in $(cat __clusterdir/nodes.lst) ; do
  echo -n $eid : 
  if [ $firstnode == yes ] ; then
    ddl="$(echo "$@" | python _plugin/spider/_script/create_table_filter.py 0 __clusterdir/nodes.lst)"
    echo $ddl
    firstnode=no
  else
    ddl="$(echo "$@" | python _plugin/spider/_script/create_table_filter.py)"
    echo $ddl
  fi
  $eid*/sql.sh "$ddl"
  [ $? -eq 0 ] && echo ok
done
