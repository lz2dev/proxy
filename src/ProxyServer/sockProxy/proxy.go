package sockProxy

import (
	"log"
	"net"
)

func Listen(addr string) {
	listener, err := net.Listen("tcp", addr) // 监听
	if err != nil {
		log.Fatalln("Error: ", err.Error())
	}
	for {
		go func(conn net.Conn, err error) {
			log.Printf("Received socket request %s %s\n", conn.LocalAddr().String(), conn.RemoteAddr().String()) // 接收到tcp连接
			if err != nil {
				log.Println("Error: ", err.Error())
				return
			}
			err = handleClientRequest(conn)
			if err != nil {
				log.Println("Error: ", err.Error())
				return
			}
		}(listener.Accept())
	}
}
