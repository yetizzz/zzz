module.exports = list

var request = require('../request')
  , current_schema

function list(site, resource) {
  site.schema(resource, done)

  function done(err, schema) {
    current_schema = schema

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

list.behaviors = {
  'click [rel=dropdown]': show_search
, 'submit [name=search]': apply_search
}

function show_search(ev) {
  console.log('wtf')

  ev.preventDefault(); ev.stopPropagation()

  var target = $(ev.target)
    , search

  target = target.is('a') ? target : target.parents('a')

  search = $(target.attr('href'))
  search.is(':visible') ? search.fadeOut('fast') : search.fadeIn('fast')

}

function apply_search(ev) {
  ev.preventDefault()

  var search = $(ev.target).find('[type=search]')

  
}

