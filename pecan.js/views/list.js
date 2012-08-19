module.exports = list

var request = require('../request')
  , scrollEnabled = false
  , debounced = null
  , current_schema
  , current_meta

function list(site, resource) {
  site.schema(resource, done)

  scrollEnabled = true
  function done(err, schema) {
    current_schema = schema

    schema.list(null, function(err, items, meta) {
      var ctxt = {
          resource: resource
        , meta: meta
        , results: items
        , schema: schema
      }

      current_meta = meta
      meta.shown = meta.offset + Math.min(meta.limit, items.length)

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

list.exit = function() {
  scrollEnabled = false
  current_meta = null
}


window.onscroll = function() {
  if(!scrollEnabled) return

  if(debounced) clearTimeout(debounced)

  debounced = setTimeout(scroll, 200)
}

function scroll() {
  if(scroll.fetching)
    return

  if(!current_meta)
    return

  if(!current_meta.next)
    return

  scroll.fetching = true

  current_schema.list(current_meta.next, function(err, items, meta) {
    current_meta = meta

    current_schema._site.cachedTemplate('list_results.html')
      .render({results: items, schema:current_schema}, function(e, d) {
        scroll.fetching = false

        $('table tbody').append(d)
      })

  })
}
