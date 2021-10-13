package blacklist

import (
	"ProxyServer/db"
	"strings"
)

func Check(host string) (bool, error) {
	host = strings.Split(host, ":")[0]
	row := db.DB.QueryRow(
		`SELECT COUNT(host) FROM blacklist
		WHERE host=?`,
		host,
	)
	var count uint
	err := row.Scan(
		&count,
	)
	if err != nil {
		return false, err
	}
	return count > 0, nil
}
