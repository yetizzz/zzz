module.exports = ResourceInstance

function ResourceInstance(data, schema) {
  this._schema = schema
  this._data = data
}

var cons = ResourceInstance
  , proto = cons.prototype

proto.fields = function() {
  var self = this
    , fieldNames = self._schema.getSortedFields()

  return fieldNames.map(function(name) {
    try {
      return [name, guard(self._data[name])]
    } catch(e) {
      return [name, self._data[name]]
    }
  })
}

proto.editor = function() {
  var self = this
    , fieldNames = self._schema.getSortedFields()
    , fields = self._schema._source.fields
    , site = self._schema._site

  return fieldNames.map(function(fieldName) {
    var meta = fields[fieldName]
      , tpl = site.cachedTemplate('widgets/'+meta.type+'.html') || site.cachedTemplate('widgets/default.html')
      , ctxt = {name: fieldName, meta: meta, value:self._data[fieldName]}
    return function(ready) {
      tpl.render(ctxt, ready)
    }
  })

}

proto.save = function(form, ready) {
  var obj = this._schema.buildFromForm(form)

  if(this.resource_uri) {
    this._schema._site.put(this.resource_uri, obj, ready) 
  } else {
    this._schema._site.post(this._schema._source.urls.list_endpoint, obj, ready)
  }
}

proto.name = function() {
  return this._data[this._schema.getSortedFields()[0]] || 'unknown'
}

function guard(datum) {
  if(typeof datum !== 'object') {
    return _($('<div />').text(datum).html())
  }

  if(!datum) {
    return _('<span class="null">null</span>')
  }

  if(Array.isArray(datum)) {
    var ul = $('<ul></ul>')
    datum.forEach(function(d) { ul.append($('<li />').html(guard(d)+'')) })
    return _('<ul>'+ul.html()+'</ul>')
  }

  var dl = $('<dl />')
  for(var key in datum) {
    var detail = $('<dt />').html(guard(datum[key]) + '')
    dl.append($('<dd />').text(key))
      .append(detail) 
  }

  return _('<dl>'+dl.html()+'</dl>')
}

function _(x) {
  x = new String(x)
  x.safe = true
  return x
}

proto.url = function() {
  return this._data.resource_uri
}
