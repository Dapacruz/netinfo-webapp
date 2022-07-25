package controllers

import (
	"context"
	"fmt"
	"github.com/go-redis/redis/v8"

	beego "github.com/beego/beego/v2/server/web"
)

type GetResults struct {
	beego.Controller
}

type GetResultsRequest struct {
	JobId string `form:"job_id"`
}

func (c *GetResults) Get() {
	ctx := context.Background()
	request := GetResultsRequest{}
    if err := c.ParseForm(&request); err != nil {
		fmt.Println(err)
	}
	rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
    })

	// Get results from Redis
	results, err := rdb.Get(ctx, request.JobId).Result()
    if err == redis.Nil {
        // fmt.Println("Key does not exist")
		// Send a 204 status code, no content
		c.Ctx.ResponseWriter.WriteHeader(204)
    } else if err != nil {
        panic(err)
    } else {
		c.Ctx.ResponseWriter.Write([]byte(results))
	}

}
