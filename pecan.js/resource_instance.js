module.exports = ResourceInstance

function ResourceInstance(data, schema) {
  this._schema = schema
  this._data = data
}

proto.fields = function() {
  var self = this
    , fieldNames = self._schema.getSortedFields()

  return fieldNames.map(function(name) {
    return [name, self._data[name]]
  })
}
