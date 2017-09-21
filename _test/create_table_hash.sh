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
PARTITION BY HASH(id + timestamp)
(
	PARTITION p0,
	PARTITION p1,
	PARTITION p2
	);
EOF
)

echo "$(echo "$ddl" | python _plugin/spider/_script/create_table_filter.py 1 "$@")"
echo "$(echo "$ddl" | python _plugin/spider/_script/create_table_filter.py 0 "$@")"
