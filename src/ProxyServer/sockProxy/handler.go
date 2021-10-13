package sockProxy

import (
	"ProxyServer/blacklist"
	"ProxyServer/transfer"
	"fmt"
	"log"
	"net"
	"strconv"
)

const BUFFER_SIZE = 4096

func handleClientRequest(client net.Conn) error {
	if client == nil {
		return nil
	}

	var buffer [BUFFER_SIZE]byte
	_, err := client.Read(buffer[:])
	if err != nil {
		return err
	}

	if buffer[0] == 0x05 { // 只处理sock5
		client.Write([]byte{0x05, 0x00})
		n, err := client.Read(buffer[:])
		if err != nil {
			return err
		}

		var host, port string
		switch buffer[3] { // 获取host地址
		case 0x01: // IPv4
			host = net.IPv4(
				buffer[4],
				buffer[5],
				buffer[6],
				buffer[7],
			).String()
		case 0x03: // 域名
			host = string(buffer[5 : n-2])
		case 0x04: // IPv6
			host = append(make(net.IP, 0, 16), buffer[4:20]...).String()
		}

		// 检查host是否在黑名单内
		inBlacklist, err := blacklist.Check(host)
		if err != nil {
			return fmt.Errorf("an error occurred while connecting to sql: %s", err.Error())
		}
		if inBlacklist {
			log.Printf("%s is in blacklist.\n", host)
			return nil
		}

		port = strconv.Itoa(int(buffer[n-2])<<8 | int(buffer[n-1]))

		server, err := net.Dial("tcp", net.JoinHostPort(host, port)) // host服务器连接
		if err != nil {
			return err
		}
		client.Write([]byte{0x05, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00})

		transferor := &transfer.TwoWayTransferor{
			Stream1: server,
			Stream2: client,
		}
		transferor.Start() // 交换客户端与host服务器数据
	}

	return nil
}
