module.exports = cookie

var cookies = (document.cookie || '').split(';').map(function(kv) {
  kv = kv.split('=')
  return [decodeURIComponent(kv[0]).replace(/(^\s+|\s+$)/g, ''), decodeURIComponent(kv.slice(1).join('=').replace(/(^\s+|\s+$)/g, ''))]
}).reduce(function(lhs, rhs) {
  lhs[rhs[0]] = rhs[1]
  return lhs
}, {})

function cookie(key) {
  return cookies[key]
}
