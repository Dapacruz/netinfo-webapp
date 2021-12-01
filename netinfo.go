package main

import (
	_ "netinfo/routers"
	beego "github.com/beego/beego/v2/server/web"
)

func main() {
	beego.Run()
}
