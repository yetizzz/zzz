module.exports = Site

var route = require('./routes')
  , request = require('./request')
  , templates = require('./templates')

function Site() {
  this.root = null
  this._tplCache = {}
}

var cons = Site
  , proto = cons.prototype

proto.init = function(body) {
  var path = window.location.pathname.slice(1).split('/')
    , basePath = path[0]
    , fn = route(path.slice(1).join('/').replace(/^\/?/, '/'))
    , self = this

  self.root = $(body)

  $('body').on('click', 'a', function(ev) {

    if(ev.target.host !== window.location.host)
      return

    ev.preventDefault()

    fn = route(ev.target.pathname)

    window.history.pushState({}, {}, '/'+basePath+ev.target.pathname)

    self.root.addClass('loading')
    fn(self)
  })

  window.onpopstate = function(ev) {
    fn = route(
      window.location.pathname.slice(1).split('/').slice(1).join('/').replace(/^\/?/, '/')
    )

    self.root.addClass('loading')
    fn(self)
  }

  fn(self) 
}

proto.render = function(name, context, ready) {
  var self = this

  self.cachedTemplate(name).render(context, function(err, data) {
    self.root.html(data)
    self.root.removeClass('loading')

    ready(null, self.root)  
  })  
}

proto.cachedTemplate = function(name) {
  var tpl = this._tplCache[name]
  if(!tpl) {
    tpl = new plate.Template(templates[name] || '')
  }
  this._tplCache[name] = tpl
  return tpl
}

proto.schema = function(name, ready) {
  var self = this
    , key = 'schema:'+name
    , schema = self.storage.get(key)
  
  if(schema) {
    return ready(null, schema)
  }

  self.schemaAll(gotSchema)

  function gotSchema(err, data) {
    if(err) return ready(err)

    if(!data[name] || !data[name].schema) {
      return ready(new Error('schema was borked'))
    }

    request.get(data[name].schema, {}, {}, function(err, data) {
      if(err) {
        return ready(err)
      }
      self.storage.set(key, data)
      return ready(null, data)
    })
  }
}

proto.schemaAll = function(ready) {
  var self = this
    , schema = self.storage.get('schema')

  if(schema)
    return ready(null, schema)

  request.get(self.apiURL(), {}, {}, function(err, data) {
    if(err) return ready(err)

    self.storage.set('schema', data)
    return ready(null, data)
  })
}

proto.apiURL = function() {
  return '/api/v1/'
}

proto.storage = {
  get: getStorage
, set: setStorage
}

function getStorage(key) {
  localStorage.getItem(key)
}

function setStorage(key, value) {
  localStorage.setItem(key, value)
}
