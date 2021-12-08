package controllers

import (
	"bytes"
	"fmt"
	"log"
	"os/exec"
	"encoding/json"

	beego "github.com/beego/beego/v2/server/web"
)

type AnalyzePath struct {
	beego.Controller
}

type AnalyzePathRequest struct {
	Source string `form:"source"`
	Destination string `form:"destination"`
}

type Response struct {
	Stderr string `json:"stderr"`
	Stdout json.RawMessage `json:"stdout"`
}

func (c *AnalyzePath) Post() {
	request := AnalyzePathRequest{}
    if err := c.ParseForm(&request); err != nil {
		fmt.Println(err)
	}

	cmd := exec.Command("static/py/netinfo.py", "--source", request.Source, "--destination", request.Destination)
	var outb, errb bytes.Buffer
	cmd.Stdout = &outb
	cmd.Stderr = &errb
	err := cmd.Run()
	if err != nil {
		log.Fatal(err)
	}

	res, err := json.Marshal(Response{errb.String(), []byte(outb.String())})
	if err != nil {
		log.Fatal(err)
	}

	// fmt.Println(string(res))
	c.Ctx.ResponseWriter.Write([]byte(res))
}
