package controllers

import (
	"bytes"
	"context"
	"os/exec"
	"fmt"
	"encoding/json"
	"github.com/go-redis/redis/v8"
	"github.com/google/uuid"
	"log"
	"time"

	beego "github.com/beego/beego/v2/server/web"
)

type AnalyzePath struct {
	beego.Controller
}

type AnalyzePathRequest struct {
	Source string `form:"source"`
	Destination string `form:"destination"`
}

type JobResults struct {
	Stderr string `json:"stderr"`
	Stdout json.RawMessage `json:"stdout"`
}

type JobDetails struct {
	JobId string `json:"jobid"`
}

func (c *AnalyzePath) Get() {
	job_id := uuid.New().String()
	request := AnalyzePathRequest{}
    if err := c.ParseForm(&request); err != nil {
		fmt.Println(err)
	}

	job_details, err := json.Marshal(JobDetails{job_id})
    if err != nil {
        panic(err)
    }

	c.Ctx.ResponseWriter.Write([]byte(job_details))

	go analyze_path(job_id, request)
}

func analyze_path(job_id string, request AnalyzePathRequest) {
	ctx := context.Background()
	rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
    })

	cmd := exec.Command("static/py/netinfo.py", "--source", request.Source, "--destination", request.Destination)
	var outb, errb bytes.Buffer
	cmd.Stdout = &outb
	cmd.Stderr = &errb
	err := cmd.Run()
	if err != nil {
		log.Fatal(err)
	}

	job_results, err := json.Marshal(JobResults{errb.String(), []byte(outb.String())})
	if err != nil {
		log.Fatal(err)
	}

	// Write results to Redis
	err = rdb.SetNX(ctx, job_id, string(job_results), 30*time.Minute).Err()
    if err != nil {
        panic(err)
    }
}
