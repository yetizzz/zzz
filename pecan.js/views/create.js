module.exports = create

var edit = require('./edit')

function create(site, resource) {
  return edit(site, resource, null)
}

create.behaviors = edit.behaviors
