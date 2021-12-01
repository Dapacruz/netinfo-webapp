package routers

import (
	"github.com/Dapacruz/netinfo/controllers"

	beego "github.com/beego/beego/v2/server/web"
)

func init() {
	beego.SetStaticPath("/static/fonts","static/fonts")
    beego.Router("/", &controllers.MainController{})
    beego.Router("/analyze/path", &controllers.AnalyzePath{})
}
