package main

import (
	"ProxyServer/httpProxy"
	"ProxyServer/sockProxy"
	"fmt"
	"sync"
)

const HTTP_PROXY_PORT uint16 = 9090
const SOCK_PROXY_PORT uint16 = 9091

func main() {
	wg := new(sync.WaitGroup)
	wg.Add(2)
	go startListenHttp(wg)
	go startListenSock(wg)
	wg.Wait()
}

// http代理，端口9090
func startListenHttp(wg *sync.WaitGroup) {
	httpProxy.Listen(fmt.Sprintf(":%d", HTTP_PROXY_PORT))
	wg.Done()
}

// sock代理，端口9091
func startListenSock(wg *sync.WaitGroup) {
	sockProxy.Listen(fmt.Sprintf(":%d", SOCK_PROXY_PORT))
	wg.Done()
}
