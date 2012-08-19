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

proto.filters = function() {
  return Object.keys(this._source.filtering || {})
}

proto.comparable = function() {
  for(var key in this._source.fields) {
    if(this._source.fields[key].type === 'datetime')
      return true
  }
  return false
}

proto.instantiable = function() {
  return this._source.allowed_detail_http_methods.indexOf('put') !== -1
}

proto.editable = function() {
  return this._source.allowed_detail_http_methods.indexOf('put') !== -1 || this._source.allowed_detail_http_methods.indexOf('post') !== -1
}

proto.deletable = function() {
  return this._source.allowed_detail_http_methods.indexOf('delete') !== -1
}

proto.viewable = function() {
  return this._source.allowed_detail_http_methods.indexOf('get') !== -1
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

proto.buildFromForm = function(form) {
  var self = this
    , fields = self._source.fields
    , output = {}
    , name
    , field

  form.find('.form-row')
      .each(function(x, el) {
        el = $(el)
        name = el.attr('data-field')
        field = fields[name]

        ;(self['handle_'+handle_field.type] || self.handle_default)(name, field, el, output)
      })
}

proto.handle_default = function(name, field, el, output) {
  output[name] = el.find('[name='+JSON.stringify(name)+']').val()
}

proto.handle_datetime = function(name, field, el, output) {

}

proto.handle_list = function(name, field, el, output) {

}

proto.handle_list_object = function(name, field, el, output) {

}

proto.handle_list_input = function(name, field, el, output) {

}



