var fs = require('fs')
  , Path = require('path')

function readTemplates(dir, ready, output) {
  output = output || []

  fs.readdir(dir, function(err, data) {
    if(err) return ready(err)

    var readyCount = data.length

    data.forEach(function(datum, idx) {
      var path = Path.join(dir, datum)

      fs.stat(path, function(err, stat) {
        if(stat.isDirectory()) return readTemplates(path, collect, output)
        
        fs.readFile(path, 'utf8', function(err, data) {
          output.push([path.split('/').slice(2).join('/'), data])
          collect()
        })
      })  
    })

    function collect() {
      !--readyCount && ready(null, output)
    }
  })
}

readTemplates('pecan.js/templates', function(e, items) {
  items = items.reduce(function(l, r) { l[r[0]] = r[1]; return l }, {})
  process.stdout.write(JSON.stringify(items))
})
