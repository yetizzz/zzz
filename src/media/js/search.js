// Taken from Read the Docs

// Searching as the user types.
(function(){

  // Save a reference to the global object.
  var root = this;

  // Global Search object on which public functions can be added
  var Search;
  Search = root.Search = {};

  // for instituting a delay between keypresses and searches
  var timer = null;
  var delay = 250;
  var lastQuery = null;
  var useApi = true;

  // Check if the browser supports history manipulation so
  // we can change the URL upon instant searches
  var replaceStateSupported = (typeof history.replaceState === "function");

  // queue of current requests
  var xhr = [];

  var $input, $project, $button, $results, $title, $selected_facets = null;
  var $search_module = null

  function init() {
    $input = $('#id_site_search_2');
    $project = $("#id_project");
    $button = $('#id_search_button');
    $results = $("#id_search_result");
    $title = $("#id_search_title");
    $selected_facets = $("#id_selected_facets");
    $search_module = $('#search_module')

    // minimum requirements for this script to kick in...
    if(!$input.length || !$results.length) {
      return false;
    } else {
      lastQuery = queryString()
      bind();
    }
  }
  Search.init = init;

  // Setup the bindings for clicking search or keypresses
  function bind() {

    // Set a delay so not _every_ keystroke sends a search
    $input.keyup(function(ev) {

      // Don't do anything unless the query has changed
      if(lastQuery == queryString()) {
        return;
      }

      if(timer) {
        clearTimeout(timer);
      }
      timer = setTimeout("Search.run()", delay);
    });

    // $button.click(Search.run);
  }

  // Abort all existing XHR requests, since a new search is starting
  function abortCurrentXHR() {
    var request = xhr.pop();
    while(request) {
      request.abort();
      request = xhr.pop();
    }
  }

  // Replace the search results HTML with `html` (string)
  function replaceResults(html) {
    $results.empty();
    $results.append(html);
    $title.html(getTitle());

    if(html.replace(/\s+/, '').length)
      $search_module.addClass('visible')
    else
      $search_module.removeClass('visible')
  }

  // Construct the results HTML
  // TODO: Use a template!
  function buildHTML(results) {
    var html = [];
    for (var i=0; i<results.length; i++) {
      obj = results[i]
      project = obj['project']
      slug = obj['slug']
      url = "/_/" + project + "/" + slug + "/"
      html.push([
        '<li class="module-item">',
          '<p class="module-item-title">',
              '<a href="', url,
                    '">',
                    slug,
          "</p>",
        "</li>"].join('')
      );
    }
    return html.join('');
  }

  // Pop the last search off the queue and render the `results`
  function onResultsReceived(results) {
    // remove the request from the queue
    xhr.pop();
    lastQuery = queryString()
    replaceResults(buildHTML(results));
    replaceState();
    $("#id_remove_facets").attr('href', removeFacetsUrl());
  }

  // Replace the URL with the one corresponding to the current search
  function replaceState() {
    if(!replaceStateSupported) {
      return;
    }
    var url = "?" + queryString();
    var title = getTitle() + " | Search";
    window.history.replaceState({}, title, url);
  }

  // Page title
  function getTitle() {
    return "Results for " + $("#id_site_search_2").val();
  }

  // Params used in the search
  function getSearchData() {
    var data = {
      slug: getKeywords(),
      project: getProject(),
    }
    return data;
  }

  // e.g. q=my+search&selected_facets=project_exact:Read%20The%20Docs
  function queryString() {
    return jQuery.param(getSearchData());
  }
  Search.queryString = queryString

  // The active query value
  function getKeywords() {
   return $input.val()
  }

  // The active query value
  function getProject() {
   return $project.val()
  }

  // Url for the current query with any facet filters removed
  function removeFacetsUrl() {
    return '?' + jQuery.param({q: getKeywords()});
  }

  // Perform the ajax request to get the search results from the API
  function run(ev) {
    if(ev) {
        ev.preventDefault();
    }
    abortCurrentXHR();

    // Don't do anything if there is no query
    if(getKeywords() == '') {
      $results.empty();
      $search_module.removeClass('visible')
      $title.html("No search term entered");
      return;
    }

    var data = getSearchData();
    if(useApi) {
        apiSearch(data);
    }

  }
  Search.run = run;

  // TODO: The api search is incomplete. It doesn't take into account
  // facets nor pagination. It's a partial implemenation.
  function apiSearch(data) {
     var project = $project[0].value
     xhr.push(jQuery.ajax({
      type: 'GET',
      url: "/_api/v1/redirect/" + project + "/",
      data: data,
      dataType: 'jsonp',
      success: function(res, text, xhqr) {
        onResultsReceived(res.objects);
      }
    }));
  }

}).call(this);
