$(function() {
  $('form[name=increment] [name=url]')
    .each(function(idx, el) {
      el = $(el)  

      var anchor = $('<a href="#"></a>')
      anchor.click(makeHandler(el))
      anchor.text(makeText(el.val()))
      anchor.insertAfter(el)
      el.hide()
    })

  function makeHandler(el) {
    return function(ev) {
      ev.preventDefault()
      el.click()
    }
  }

  function makeText(text) {
    var a = document.createElement('a')

    a.href = text
    return a.pathname
  }
})
