package controllers

import (
	"bytes"
	"fmt"
	"log"
	"os/exec"

	beego "github.com/beego/beego/v2/server/web"
)

type AnalyzePath struct {
	beego.Controller
}

type AnalyzePathRequest struct {
	Source string `form:"source"`
	Destination string `form:"destination"`
}

func (c *AnalyzePath) Post() {
	request := AnalyzePathRequest{}
    if err := c.ParseForm(&request); err != nil {
		fmt.Println(err)
	}

	fmt.Println(request.Source)
	fmt.Println(request.Destination)

	cmd := exec.Command("static/py/netinfo.py", "--source", request.Source, "--destination", request.Destination)
	var outb, errb bytes.Buffer
	cmd.Stdout = &outb
	cmd.Stderr = &errb
	err := cmd.Run()
	if err != nil {
		fmt.Println(errb.String())
		log.Fatal(err)
	}

	fmt.Println("out:", outb.String(), "err:", errb.String())

	c.Ctx.ResponseWriter.Write([]byte(outb.String()))
}
