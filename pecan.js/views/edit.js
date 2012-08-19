module.exports = edit

function edit(site, resource, full_resource) {
  var ctxt = {}

  full_resource = full_resource ? full_resource.replace(/\/?$/, '/') : ''

  site.schema(resource, function(err, schema) {
    ctxt.schema = schema

    if(full_resource)
      schema.get(full_resource, got_instance)
    else
      got_instance(null, schema.instantiate())
  })

  function got_instance(err, instance) {
    // alright
    ctxt.resource = resource
    ctxt.instance = instance

    site.render('edit.html', ctxt, function(err, data) {
    })
  }
}

edit.behaviors = {
    'click [rel=delete]': delete_instance
  , 'submit form':        save_instance
}

function delete_instance(ev) {

}

function save_instance(ev) {

}
