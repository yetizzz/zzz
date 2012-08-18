module.exports = list

var request = require('../request')

function list(site, resource) {
  site.schemaAll(done)

  function done(err, schemas) {
    var schema = schemas[resource]

    request.get(schema.list_endpoint, {}, {}, function(err, items) {
      site.render('list.html', {results: items}, function(err, el) {

      })
    })    
  }
}
