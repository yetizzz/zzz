module.exports = scaffold

var plate = require('plate')
  , templates = require('./templates')

function scaffold(ready) {
  new plate.Template(templates['initial.html']).render({}, function(err, html) {
    if(err) {
      return ready(err)
    }
    document.body.innerHTML = html
    ready(null)
  })
}

scaffold.templates = templates
