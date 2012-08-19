module.exports = edit

var current_instance
  
function edit(site, resource, full_resource) {
  var ctxt = {}
    , is_new = !full_resource

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
    ctxt.is_new = is_new
    current_instance = instance

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
  ev.preventDefault()

  current_instance.save($('form'), function(err, data) {
    if(err) {
      $('body').addClass('error')
      $('[name=error]').text(err.message)

      return setTimeout(function() { $('body').removeClass('error') }, 5000)
    }
    
    alert('yay you saved it') 
  })  
}
