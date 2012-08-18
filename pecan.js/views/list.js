module.exports = list

var request = require('../request')

function list(site, resource) {
  site.schema(resource, done)

  function done(err, schema) {

    schema.list(null, function(err, items, meta) {
      var ctxt = {
          resource: resource
        , meta: meta
        , results: items
        , schema: schema
      }

      site.render('list.html', ctxt, function(err, el) {

      })
    })    
  }
}
