# mariadb-environs-spider
plugin for mariadb-environs

## Friendly Spider sharding tutorial with Environs Framework preview

Steps:
1. Setup default Environs cluster (includes downloading of MariaDB 10.2.6 tar.gz)
2. Setup Spider
3. Test inserts
4. Replace one node for debugging
5. Replace one node with different vendor
6. Make sure that Spider is still working properly

This article assumes that readers already know at least theoretical details of Spider idea and preferably want to set up demo Spider cluster in an easy way.

Yes, there are many Spider tutorials already, but this one will attempt to demonstrate trade between power / flexibility / simplicity which comes with Environs framework.

The reader is welcome to attempt to use the commands below in most of Linux environments (with bash4, python and few more core utils) and give any feedback about the process.
Steps 1-3 are more dedicated to Spider smoke test
Steps 4-6 demonstrate some additional features of Environs Framework

### Step 1. Setup default Environs cluster (includes downloading of MariaDB 10.2.6 tar.gz)

```
git clone http://github.com/AndriiNikitin/mariadb-environs
cd mariadb-environs
./get_plugin.sh spider
_template/plant_cluster.sh cluster1
cat cluster1/nodes.lst
cluster1/replant.sh 10.2.6
m0*/download.sh
cluster1/gen_cnf.sh
cluster1/install_db.sh
cluster1/startup.sh
```
Four nodes should be up and running. Let's name them m0, m1, m2 and m3. At the moment they are just plain default MariaDB Server instances (thus "cluster" only in logical sense). Next step will be to init Spider plugin on m0 and create corresponding shard tables on each node according to documentation. (where m0 will be primary Spider node and the rest - shards).

### Step 2. Setup Spider
```
m0*/sql.sh source _plugin/spider/_script/install_spider.sql
# let's create partitioned table definition which will be sharded between 3 nodes
tee ddl.sql <<EOF
CREATE TABLE test.log
(
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        timestamp DATETIME NOT NULL,
        user INT UNSIGNED,
        ip BINARY(16) NOT NULL,
        action VARCHAR(20) NOT NULL,
        PRIMARY KEY (id, timestamp)
)
        ENGINE = InnoDB
PARTITION BY RANGE (YEAR(timestamp))
(
        PARTITION p0 VALUES LESS THAN (2010),
        PARTITION p1 VALUES LESS THAN (2014),
        PARTITION p3 VALUES LESS THAN (2020)
);
EOF
# now create corresponding tables on the nodes:
cluster1/spider_create_table_filter_execute.sh "$(cat ddl.sql)"

# verify the tables are correct
# first entry should show correct Spider definition,
# the rest - the same table table without partitions
cluster1/sql.sh show create table test.log
```

### Step 3. Test inserts
Let's insert some data on m0 and check what exists on the rest
```
m0*/sql.sh "insert into test.log select null, adddate(now(),-10*365), 1, 1, 1"
cluster1/sql.sh "select count(*) from test.log"
m0*/sql.sh "insert into test.log select null, adddate(now(),-5*365), 2, 2, 2"
cluster1/sql.sh "select count(*) from test.log"
m0*/sql.sh "insert into test.log select null, now(), 3, 3, 3"
cluster1/sql.sh "select count(*) from test.log"
```
### Step 4. Replace one node for debugging
Cool, I hope the cluster is working properly and the queries above did confirm expectations. Now let's play with the framework more.
E.g. let's assume we have some failing test case and want to try the same on a node from latest 10.2 development tree.

Before that let's create a physical backup of m3 node (using xtrabackup). Thus we will need to download desired xtrabackup version:

```
./get_plugin.sh xtrabackup
./replant.sh x1-2.4.7
x1*/download.sh

mkdir -p backup/m3
x1*/backup.sh m3 backup/m3

# backup is ready, now replace tar from m3 with instance built from source code
./replant.sh m3-10.2
./build_or_download.sh m3
cp -R backup/m3/* m3*/dt
m3*/gen_cnf.sh
m3*/startup.sh

# new node is in place, let's make sure that everything is ok
cluster1/status.sh
cluster1/sql.sh "select version()"
```
### Step 5. Replace one node with different vendor
Let's assume we are still unlucky with troubleshooting and want to check node behaviour with Oracle MySQL binary. (will download and unpack 5.7.18 tar)

```
./get_plugin.sh oracle-mysql
./replant.sh o1-5.7.18
o1*/download.sh
o1*/gen_cnf.sh
o1*/install_db.sh
o1*/startup.sh

# Oracle MySQL instance is up and running.
# Let's use mysqldump this time to backup and replace m2 node.

mkdir -p backup/m2
m2*/dump.sh test > backup/m2/dump.sql
o1*/sql.sh source backup/m2/dump.sql

# now we must make sure that o1 instance will run on the same node as m2
o1*/shutdown.sh
sed -i "s/\s*port\s*=.*/port=$(m2*/sql.sh select @@port)/" o1*/my.cnf 
m2*/shutdown.sh
o1*/startup.sh

# replace node in cluster
sed -i '/m2/ s/m2/o1/' cluster1/nodes.lst
# check cluster status
cluster1/status.sh
cluster1/sql.sh "select version()"
```
### Step 6. Make sure that Spider is still working properly
```
cluster1/sql.sh "select count(*) from test.log"
m0*/sql.sh truncate test.log
cluster1/sql.sh "select count(*) from test.log"
m0*/sql.sh "insert into test.log select null, adddate(now(),-10*365), 1, 1, 1"
cluster1/sql.sh "select count(*) from test.log"
m0*/sql.sh "insert into test.log select null, adddate(now(),-5*365), 2, 2, 2"
cluster1/sql.sh "select count(*) from test.log"
m0*/sql.sh "insert into test.log select null, now(), 3, 3, 3"
cluster1/sql.sh "select count(*) from test.log"
```
### Summary
In this tutorial we performed smoke test of simplest Spider sharding cluster on single machine, using some practical features of MariaDB Environs Framework

For reference below are:
[script with all commands above](https://github.com/AndriiNikitin/mariadb-environs-spider/blob/master/_script/example.sh)

[script will create docker file and build docker image which demonstrates this example](https://github.com/AndriiNikitin/mariadb-environs-spider/blob/master/_script/example_in_docker.sh)

[As well as reference to corresponding travis test](https://travis-ci.org/AndriiNikitin/mariadb-environs-spider)
