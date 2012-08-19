module.exports = route

var views = require('./views')

function route(path) { 
  var match

  for(var i = 0, len = route.routes.length; i < route.routes.length; ++i) {
    if(match = route.routes[i][0].exec(path)) {
      var target = route.routes[i][1]
        , ret = function() { target.apply(null, [].slice.call(arguments).concat(match.slice(1))) }

      for(var key in target) {
        ret[key] = target[key]
      }
      ret._name = target.name
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

route.routes.forEach(function(tuple) {
  var view = tuple[1]
    , behaviors = view.behaviors || {}
    , root = $(':root')

  for(var key in behaviors) {
    key = key.split(' ')

    root.on(key[0], '.view_'+view.name+' '+key[1], behaviors[key.join(' ')])
  }
})
