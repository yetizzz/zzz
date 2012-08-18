var Site = require('./index')
  , scaffold = require('./scaffold')
  , site

scaffold(function(err, ready) {
  site = new Site()
  site.init('body', scaffold.templates)
})
