#!/bin/bash
for eid in $(cat __clusterdir/nodes.lst) ; do
  echo -n $eid : 
  ddl="$(echo "$@" | python _plugin/spider/create_table_filter.py "$([[ $eid =~ 0 ]] && echo 0)")"
  $eid*/sql.sh "$ddl"
  [ $? -eq 0 ] && echo ok
done
