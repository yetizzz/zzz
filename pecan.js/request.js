module.exports = request

function request(method, path, headers, body, ready) {
  $.ajax({
      type: method
    , url: path
    , headers: headers
    , data: ['POST', 'PUT', 'PATCH'].indexOf(method) !== -1 ? JSON.stringify(body) : ''
    , contentType: 'application/json'
    , success: ready.bind(null, null)
    , error: function(_, __, err) { ready(err) }
  })
}

;['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD'].map(function(x) {
  request[x.toLowerCase()] = request.bind(null, x)
})
