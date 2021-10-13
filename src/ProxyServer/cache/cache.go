package cache

import (
	"ProxyServer/db"
	"crypto/md5"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
)

type CacheStatus struct {
	Header     http.Header
	StatusCode int
}

type Cache struct {
	CacheStatus
	Body []byte
}

var suffixes []string = []string{
	".php",
	".jsp",
	".asp",
	".aspx",

	".jpg",
	".png",
	".bmp",
	".mp4",
}

// 获取请求的md5校验值
func GetAbstract(r *http.Request) ([16]byte, error) {
	isStatic := false
	for _, suffix := range suffixes {
		if strings.HasSuffix(r.RequestURI, suffix) {
			isStatic = true
			break
		}
	}

	var abstract [16]byte
	if isStatic {
		abstract = md5.Sum([]byte(r.RequestURI))
	} else {
		abstract = [16]byte{}
	}

	// log.Println(hex.EncodeToString(abstract[:]))
	return abstract, nil
}

// 获取缓存
func Get(abstract [16]byte) *Cache {
	if abstract == [16]byte{} {
		return nil
	}
	row := db.DB.QueryRow(
		`SELECT file FROM cache
		WHERE Cid=?`,
		abstract[:],
	)
	var cacheName string
	err := row.Scan(
		&cacheName,
	)
	if err != nil {
		if err != sql.ErrNoRows {
			log.Println("Error: ", err.Error())
		}
		return nil
	}

	cacheStatusFile, err := os.OpenFile(
		cacheName+".status",
		os.O_RDONLY,
		0666,
	)
	if err != nil {
		log.Println("Error: ", err.Error())
		return nil
	}
	defer cacheStatusFile.Close()
	cacheStatus, err := io.ReadAll(cacheStatusFile)
	if err != nil {
		log.Println("Error: ", err.Error())
		return nil
	}
	cacheData := new(Cache)
	err = json.Unmarshal(cacheStatus, &cacheData.CacheStatus)
	if err != nil {
		log.Println("Error: ", err.Error())
		return nil
	}

	cacheFile, err := os.OpenFile(
		cacheName,
		os.O_RDONLY,
		0666,
	)
	if err != nil {
		log.Println("Error: ", err.Error())
		return nil
	}
	defer cacheFile.Close()
	cacheData.Body, err = io.ReadAll(cacheFile)
	if err != nil {
		log.Println("Error: ", err.Error())
		return nil
	}

	log.Printf("Got cache %x.\n", abstract)
	return cacheData
}

// 保存缓存
func Save(abstract [16]byte, cache *Cache) {
	if abstract == [16]byte{} {
		return
	}
	_, err := os.Stat("CacheFiles")
	if err != nil {
		if os.IsNotExist(err) {
			err := os.Mkdir("CacheFiles", 0777)
			if err != nil {
				log.Println("Error: ", err.Error())
				return
			}
		} else {
			log.Println("Error: ", err.Error())
			return
		}
	}

	cacheName := "CacheFiles/" + hex.EncodeToString(abstract[:])

	cacheStatusFile, err := os.OpenFile(
		cacheName+".status",
		os.O_WRONLY|os.O_TRUNC|os.O_CREATE,
		0666,
	)
	if err != nil {
		log.Println("Error: ", err.Error())
		return
	}
	cacheStatus, err := json.Marshal(cache.CacheStatus)
	if err != nil {
		log.Println("Error: ", err.Error())
		return
	}
	_, err = cacheStatusFile.Write(cacheStatus)
	if err != nil {
		log.Println("Error: ", err.Error())
		cacheStatusFile.Close()
		return
	}
	err = cacheStatusFile.Close()
	if err != nil {
		log.Println("Error: ", err.Error())
		return
	}

	cacheFile, err := os.OpenFile(
		cacheName,
		os.O_WRONLY|os.O_TRUNC|os.O_CREATE,
		0666,
	)
	if err != nil {
		log.Println("Error: ", err.Error())
		return
	}
	_, err = cacheFile.Write(cache.Body)
	if err != nil {
		log.Println("Error: ", err.Error())
		cacheFile.Close()
		return
	}
	err = cacheFile.Close()
	if err != nil {
		log.Println("Error: ", err.Error())
		return
	}

	result, err := db.DB.Exec(
		`INSERT INTO cache (Cid, file)
		VALUES (?, ?);`,
		abstract[:],
		cacheName,
	)
	if err != nil {
		log.Println("Error: ", err.Error())
		return
	}
	affected, err := result.RowsAffected()
	if err != nil {
		log.Println("Error: ", err.Error())
		return
	}
	if affected == 0 {
		log.Println("Error: ", errors.New("affected 0 rows"))
		return
	}
}
