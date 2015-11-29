(function(window) {
  window.ajax = {
    getJSON: function(url, callback) {
      var xhr;
      if (typeof XMLHttpRequest !== 'undefind') {
        xhr = new XMLHttpRequest();
      } else {
        var versions = [
          'MSXML2.XmlHttp.5.0',
          'MSXML2.XmlHttp.4.0',
          'MSXML2.XmlHttp.3.0',
          'MSXML2.XmlHttp.2.0',
          'Microsoft.XmlHttp'
        ];
        for (var i = 0; i < versions.length; i++) {
          try {
            xhr = new window.ActiveXObject(versions[i]);
          } catch (err) {
            console.log(err);
          }
        }
      }

      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status == 200) {
          var data = JSON.parse(xhr.responseText);
          callback(data);
        }
      };

      xhr.open('GET', url, true);
      xhr.send('');
      return xhr;
    }
  };
})(window);
