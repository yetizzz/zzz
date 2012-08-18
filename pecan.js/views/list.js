module.exports = list

var request = require('../request')

function list(site, resource) {
  site.schemaAll(done)

  function done(err, schemas) {
    var schema = schemas[resource]

    request.get(schema.list_endpoint, {}, {}, function(err, items) {
      items.objects = items.objects.map(getName.bind(schema))

      site.render('list.html', {resource: resource, results: items}, function(err, el) {

      })
    })    
  }
}

function getName(obj, idx, all) {
  for(var i = 0, len = names.length; i < len; ++i) {
    if(obj[names[i]]) {
      obj.__name__ = obj[names[i]]
      return obj
    }
  }
  
  for(var key in this) {
    if(this[key].type === 'string') {
      obj.__name__ = obj[this[key]]
      return obj
    }
  }

  obj.__name__ = resource_uri

  return obj
}

var names = [
    'name'
  , 'display_name'
  , 'human_name'
  , 'title'
  , 'slug'
]
