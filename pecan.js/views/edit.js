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
  , 'change [name=mode]': select_new_mode
  , 'click [rel=add]': dispatch_add
  , 'click [rel=remove]': dispatch_remove
}

function delete_instance(ev) {
  ev.preventDefault()

  current_instance.delete(function(err) {
    // deleting! 
  }) 
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

function select_new_mode(ev) {
  var el = $(ev.target)
    , mode = el.val()

  var next = el.nextAll('[name='+mode+']').html()

  el.parent()
    .html('')
    .append(next)
}

function remove_key_value(ev) {
  ev.preventDefault()

  var el = $(ev.target)

  el.parents('.key-value-row')
    .remove()

}

function add_key_value(ev) {
  ev.preventDefault()

  var el = $(ev.target)
    , root = el.parents('.key-value')
    , rows = root.find('.key-value-row')
    , row = rows.eq(0).clone()

  row.find(':input').each(function(x, e) { $(e).val(null) })
  row.insertAfter(rows.eq(rows.length-1))
}

function add_list_value(ev) {
  ev.preventDefault()

  var el = $(ev.target)
    , root = el.parents('.value')
    , row = root.clone()

  row.find(':input').each(function(x, e) { $(e).val(null) })
  row.insertAfter(root)
}

function remove_list_value(ev) {
  ev.preventDefault()

  var el = $(ev.target)

  el.parents('.value')
    .remove()
}

function dispatch_add(ev) {
  var el = $(ev.target)

  el = el.is('a') ? el : el.parents('a')

  if(el.parents('.key-value').length)
    return add_key_value(ev)
  return add_list_value(ev)
}

function dispatch_remove(ev) {
  var el = $(ev.target)

  el = el.is('a') ? el : el.parents('a')

  if(el.parents('.key-value-row').length)
    return remove_key_value(ev)
  return remove_list_value(ev)

}


