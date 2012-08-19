module.exports = Schema

var ResourceInstance = require('./resource_instance')

function Schema(name, obj, site) {
  this._source = obj
  this._site = site
  this._name = name
  this._sortedFieldsCache = null
}

var cons = Schema
  , proto = cons.prototype

proto.getSortedFields = function() {
  if(this._sortedFieldsCache)
    return this._sortedFieldsCache

  // name first, then everything else
  var names = [
      'display_name'
    , 'human_name'
    , 'title'
    , 'name'
    , 'slug'
  ]

  var name_field

  for(var i = 0, len = names.length; i < len; ++i) {
    if(this._source.fields[names[i]]) {
      name_field = names[i]
      break
    }
  }
  
  if(!name_field)
  for(var key in this._source.fields) {
    if(this._source.fields[key].type === 'string') {
      name_field = key
      break
    }
  }

  var fields = !name_field ? 
    Object.keys(this._source.fields)
        .filter(function(x) { return x !== name_field && x !== 'resource_uri' }) :
    [name_field].concat(
      Object.keys(this._source.fields)
        .filter(function(x) { return x !== name_field && x !== 'resource_uri' })
    )

  return this._sortedFieldsCache = fields
}

proto.wrap = function(result) {
  return new ResourceInstance(result, this)
}

proto.instantiable = function() {
  
}

proto.editable = function() {

}

proto.deletable = function() {

}

proto.viewable = function() {

}

proto.instantiate = function() {
  var obj = {}
  for(var key in this._source.fields) {
    obj[key] = this._source.fields.default !== 'No default provided.' ? this._source.fields.default : default_for_type(this._source.fields.type)
  }

  return new ResourceInstance(obj, this)

  function default_for_type(type) {
    switch(type) {
      case 'list': return []
      case 'integer': return 0
      case 'string': return ''
      case 'datetime': return new Date().toISOString()
    }
    return ''
  }
}

proto.get = function(url, ready) {
  var self = this

  self._site.resourceInstance(url, function(err, data) {
    ready(null, self.wrap(data))
  })
}

proto.list = function(url, ready) {
  var self = this

  url = url || self._source.urls.list_endpoint

  self._site.schemaResources(url, function(err, data) {
    if(err) return ready(err)

    ready(null, data.objects.map(self.wrap.bind(self)), data.meta)
  })
}
