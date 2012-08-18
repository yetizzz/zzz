module.exports = root

function root(site) {
  site.schemaAll(function(err, data) {
    site.render('root.html', {results: data}, function(err, el) {
      
    })
  })
}
