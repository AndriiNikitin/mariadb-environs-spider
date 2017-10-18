#!/bin/bash
table_ddl="$@"
set -e
[ ! -z "$table_ddl" ] || exit 1

# this includes "partition by" , so one more than needed
partition_count=$(echo "$table_ddl" | grep -i -c "\<partition\>")
# let partition_count=partition_count-1

while [  "$partition_count" -ge 1 ]; do
  let partition_count=partition_count-1 || :
  __workdir/sql.sh "$(echo "$table_ddl" | __workdir/../_plugin/spider/_script/create_table_filter.py $partition_count __wwid)"
done

:
