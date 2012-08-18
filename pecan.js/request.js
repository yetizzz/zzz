module.exports = request

var $ = require('jquery')

function request(method, path, headers, body, ready) {
  $.ajax({
      type: method
    , url: path
    , headers: headers
    , data: body
    , success: ready.bind(null, null)
    , error: function(_, __, err) { ready(err) }
  })
}

;['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD'].map(function(x) {
  request[x.toLowerCase()] = request.bind(null, x)
})
