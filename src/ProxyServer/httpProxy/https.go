package httpProxy

import (
	"ProxyServer/transfer"
	"net"
	"net/http"
	"time"
)

func httpsHandler(
	w http.ResponseWriter,
	r *http.Request,
) {
	destConn, err := net.DialTimeout("tcp", r.Host, 60*time.Second) // host服务器连接
	if err != nil {
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)

	hijacker, ok := w.(http.Hijacker)
	if !ok {
		http.Error(w, "Hijacking not supported", http.StatusInternalServerError)
		return
	}

	clientConn, _, err := hijacker.Hijack() // 客户端连接
	if err != nil {
		http.Error(w, err.Error(), http.StatusServiceUnavailable)
	}
	transferor := &transfer.TwoWayTransferor{
		Stream1: destConn,
		Stream2: clientConn,
	}
	transferor.Start() // 交换客户端与host服务器数据
}
