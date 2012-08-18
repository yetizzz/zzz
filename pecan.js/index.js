module.exports = Site

var route = require('./routes')
  , request = require('./request')
  , templates = require('./templates')
  , Schema = require('./schema')

function Site() {
  this.root = null
  this._tplCache = {}
  this._auth = {}
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

      fn = route(path)

      fn(self) 

      return '/'+first_bit+'/'+(path ? path.replace(/\/?$/, '/') : '')
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
     
      var val = self._apiURL = form.find('[name=root_url]').val()

      console.log(val)
      self.storage.set('rooturl', val)
      self.storage.set('auth', btoa(form.find('[name=user]').val()+':'+form.find('[name=password]')))
      return ready(null, val)
    })
  })
}

proto.schema = function(name, ready) {
  var self = this
    , key = 'schema:'+name
    , schema = self.storage.get(key)
  
  if(schema) {
    return ready(null, new Schema(name, schema, self))
  }

  self.schemaAll(gotSchema)

  function gotSchema(err, data) {
    if(err) return ready(err)

    if(!data[name] || !data[name].schema) {
      return ready(new Error('schema was borked'))
    }

    request.get(data[name].schema, self.authHeader(), {}, function(err, schemaData) {
      if(err) {
        return ready(err)
      }

      schemaData.urls = data[name]

      self.storage.set(key, schemaData)
      return ready(null, new Schema(name, schemaData, self))
    })
  }
}

proto.schemaAll = function(ready) {
  var self = this
    , schema = self.storage.get('schema')

  if(schema)
    return ready(null, schema)

  request.get(self.apiURL(), self.authHeader(), {}, function(err, data) {
    if(err) return ready(err)

    self.storage.set('schema', data)

    return ready(null, data)
  })
}

proto.schemaResources = function(url, ready) {
  request.get(url, this.authHeader(), {}, ready)
}

proto.authHeader = function() {
  return {
    'Authorization': 'Basic '+this.storage.get('auth')
  }
}

proto.apiURL = function() {
  return this._apiURL
}

if(true) {
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
  return JSON.parse(localStorage.getItem(key))
}

function setStorage(key, value) {
  localStorage.setItem(key, JSON.stringify(value))
}
