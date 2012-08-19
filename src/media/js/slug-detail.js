$(function() {
  $('form[name=increment] [name=url]')
    .each(function(idx, el) {
      el = $(el)  

      var anchor = $('<a href="#"></a>')
      anchor.click(makeHandler(el))
      anchor.text(makeText(el.val()))
      anchor.insertAfter(el)
      anchor.attr('title', el.val())
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
    var link =  a.pathname + a.hash
    if(link.length > 80) {
      link = '...' + link.slice(-80)
    }

    return link
  }
})
