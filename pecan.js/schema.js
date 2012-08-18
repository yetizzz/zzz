module.exports = Schema

var ResourceInstance = require('./resource_instance')

function Schema(obj) {
  this._source = obj
}

var cons = Schema
  , proto = cons.prototype

proto.getSortedFields = function() {
  // name first, then everything else
}

proto.wrap = function(result) {

}

proto.instantiable = function() {

}

proto.editable = function() {

}

proto.deletable = function() {

}

proto.viewable = function() {

}
