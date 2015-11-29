(function(window, autocomplete, ajax) {
  function findElements(attribute) {
    var matching = [];
    var elements = document.getElementsByTagName('*');
    for (var i = 0; i < elements.length; i++) {
      if (elements[i].getAttribute(attribute) !== null) {
        matching.push(elements[i]);
      }
    }
    return matching;
  }

  document.addEventListener('DOMContentLoaded', function() {
    var suggestions = findElements('data-suggest');
    if (suggestions.length) {
      var xhr;
      var results = {};
      var suggestion = suggestions[0];
      new autocomplete({
        selector: 'input[data-suggest]',
        minChars: 2,
        source: function(term, response) {
          try {
            xhr.abort();
          } catch(e) { }
          var url = '/search?q=';
          url += encodeURIComponent(term);
          url += '&resource=' + suggestion.getAttribute('data-resource');
          xhr = ajax.getJSON(url, function(data) {
            var names = [];
            results = {};
            for (var i = 0; i < data.items.length; i++) {
              var item = data.items[i];
              results[item['name']] = item['_id'];
              names.push(item['name']);
            }
            response(names);
          });
        },
        onSelect: function(e, term, item) {
          var url = suggestion.getAttribute('data-url');
          var target = suggestion.getAttribute('data-target');
          var id = results[term];
          url = url.replace('{}', id);
          target = document.getElementById(target);
          target.href = url;
        }
      });
    }
  }, false);
})(window, window.autoComplete || {}, window.ajax || {});
