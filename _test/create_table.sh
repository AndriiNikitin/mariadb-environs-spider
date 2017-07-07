ddl=$(cat << EOF
CREATE TABLE log
(
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	timestamp TIMESTAMP NOT NULL,
	user INT UNSIGNED,
	ip BINARY(16) NOT NULL,
	action VARCHAR(20) NOT NULL,
	PRIMARY KEY (id, timestamp)
)
	ENGINE = InnoDB
PARTITION BY RANGE (UNIX_TIMESTAMP(timestamp))
(
	PARTITION p0 VALUES LESS THAN (UNIX_TIMESTAMP('2014-08-01 00:00:00')),
	PARTITION p1 VALUES LESS THAN (UNIX_TIMESTAMP('2014-11-01 00:00:00')),
	PARTITION p2 VALUES LESS THAN (UNIX_TIMESTAMP('2015-02-01 00:00:00'))
);
EOF
)

echo "$(echo "$ddl" | python _plugin/spider/create_table_filter.py)"
echo "$(echo "$ddl" | python _plugin/spider/create_table_filter.py 0)"
