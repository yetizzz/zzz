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
  var self = this

  self.root = $(body)

  self.getRootURL(function(err, url) {
    $('body').on('click', 'a', function(ev) {
      if(ev.target.host !== window.location.host)
        return

      ev.preventDefault()

      window.history.pushState({}, {}, please_route(ev.target.pathname))

      self.root.addClass('loading')
      fn(self)
    })

    window.onpopstate = function(ev) {
      please_route(window.location.pathname)
      self.root.addClass('loading')
      fn(self)
    }

    please_route(window.location.pathname)

    function please_route(path) {
      var first_bit = /^\/([^\/]+)\//g.exec(path)[1]

      path = path
        .replace(/^\/([^\/]+)\//g, '')
        .replace(/\/?/, '/')

      fn = route(path)
      console.log('routing...', path, fn.name)

      fn(self) 

      return '/'+first_bit+path
    }
  })
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

proto.getRootURL = function(ready) {
  var self = this
    , url = self.storage.get('rooturl')

  if(url) {
    return ready(null, url)
  }

  self.render('root_url_dialog.html', {}, function(err, el) {
    var form = el.find('form')
    
    form.submit(function(ev) {
      ev.preventDefault()
      
      return ready(null, self._apiURL = form.find('[name=root_url]').val())
    })
  })
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
  return this._apiURL
}

if(false) {
  proto.storage = {
    get: getStorage
  , set: setStorage
  }
} else {
  proto.storage = {
    get: getEphemeral
  , set: setEphemeral
  }
}

function getEphemeral(key) {
  return this[key]
}

function setEphemeral(key, val) {
  this[key] = val
}

function getStorage(key) {
  localStorage.getItem(key)
}

function setStorage(key, value) {
  localStorage.setItem(key, value)
}
