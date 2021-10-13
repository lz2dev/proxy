package httpProxy

import (
	"ProxyServer/cache"
	"io"
	"log"
	"net"
	"net/http"
	"strings"
)

func httpHandler(
	w http.ResponseWriter,
	r *http.Request,
) {
	abstract, err := cache.GetAbstract(r)
	var requestCache *cache.Cache = nil
	if err == nil {
		requestCache = cache.Get(abstract) // 获取缓存
	}

	// 没有缓存则转发请求，并保存缓存
	if requestCache == nil {
		transport := http.DefaultTransport
		request := new(http.Request)
		*request = *r // 复制一份请求，发送给host服务器

		if clientIP, _, err := net.SplitHostPort(r.RemoteAddr); err == nil {
			if prior, ok := request.Header["For"]; ok {
				clientIP = strings.Join(prior, ", ") + ", " + clientIP
			}
			request.Header.Set("For", clientIP)
		} else {
			log.Println("Error: ", err.Error())
			w.WriteHeader(http.StatusBadGateway)
			return
		}

		response, err := transport.RoundTrip(request) // 获取host服务器响应
		if err != nil {
			log.Println("Error: ", err.Error())
			w.WriteHeader(http.StatusBadGateway)
			return
		}
		header := response.Header
		statusCode := response.StatusCode
		body, err := io.ReadAll(response.Body)
		if err != nil {
			log.Println("Error: ", err.Error())
			w.WriteHeader(http.StatusBadGateway)
			return
		}
		err = response.Body.Close()
		if err != nil {
			log.Println("Error: ", err.Error())
		}
		requestCache = &cache.Cache{
			CacheStatus: cache.CacheStatus{
				Header:     header,
				StatusCode: statusCode,
			},
			Body: body,
		}

		go cache.Save(abstract, requestCache) // 保存缓存
	}

	h := w.Header()
	for key, value := range requestCache.Header {
		for _, v := range value {
			h.Add(key, v)
		}
	}
	w.WriteHeader(requestCache.StatusCode) // 将host服务器响应转发回客户端
	_, err = w.Write(requestCache.Body)
	if err != nil {
		log.Println("Error: ", err.Error())
		w.WriteHeader(http.StatusBadGateway)
		return
	}
}
