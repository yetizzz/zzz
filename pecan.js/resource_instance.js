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
    return _(ul.html())
  }

  var dl = $('<dl />')
  for(var key in datum) {
    var detail = $('<dt />').html(guard(datum[key]) + '')
    dl.append($('<dd />').text(key))
      .append(detail) 
  }

  return _(dl.html())
}

function _(x) {
  x = new String(x)
  x.safe = true
  return x
}

proto.url = function() {
  return this._data.resource_uri
}
