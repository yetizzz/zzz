module.exports = route

var views = require('./views')

function route(path) { 
  var match

  path = path.slice(1).split('/').slice(1).join('/')

  console.log(path)
  for(var i = 0, len = route.routes.length; i < route.routes.length; ++i) {
    if(match = route.routes[i][0].exec(path)) {
      return function() { route.routes[i][1].apply(null, [].slice.call(arguments).concat(match.slice(1))) } 
    } 
  }
}

route.routes = [
    [/^\/?$/, views.root]
  , [/^(.*?)/, views.list]
  , [/^(.*?)\/_\/new/, views.create]
  , [/^(.*?)\/_\/(.*?)/, views.edit]
]
