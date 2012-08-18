module.exports = route

var views = require('./views')

function route(path) { 
  var match

  for(var i = 0, len = route.routes.length; i < route.routes.length; ++i) {
    if(match = route.routes[i][0].exec(path)) {
      var ret = function() { route.routes[i][1].apply(null, [].slice.call(arguments).concat(match.slice(1))) }

      ret.name = route.routes[i][1].name
      return ret 
    } 
  }
}

route.routes = [
    [/^$/, views.root]
  , [/^([^\/]+)\/_\/new\//, views.create]
  , [/^([^\/]+)\/_\/(.*)\//, views.edit]
  , [/^([^\/]+)\//, views.list]
]
