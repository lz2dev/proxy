package transfer

import (
	"io"
	"sync"
)

type OneWayTransferor struct {
	Destination io.WriteCloser
	Source      io.ReadCloser
}

func (t OneWayTransferor) Start() {
	defer t.Destination.Close()
	defer t.Source.Close()
	wg := new(sync.WaitGroup)
	wg.Add(1)
	go transfer(t.Destination, t.Source, wg)
	wg.Wait()
}

type TwoWayTransferor struct {
	Stream1 io.ReadWriteCloser
	Stream2 io.ReadWriteCloser
}

func (t TwoWayTransferor) Start() {
	defer t.Stream1.Close()
	defer t.Stream2.Close()
	wg := new(sync.WaitGroup)
	wg.Add(2)
	go transfer(t.Stream1, t.Stream2, wg)
	go transfer(t.Stream2, t.Stream1, wg)
	wg.Wait()
}

func transfer(destination io.Writer, source io.Reader, wg *sync.WaitGroup) {
	io.Copy(destination, source)
	wg.Done()
}
