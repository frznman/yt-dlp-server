  // requires jQuery ... for now

function ToastBuilder(options) {
  // options are optional
  var opts = options || {};
  
  // setup some defaults
  opts.defaultText = opts.defaultText || 'default text';
  opts.displayTime = opts.displayTime || 3000;
  opts.target = opts.target || 'body';

  return function (text) {
    $('<div/>')
      .addClass('toast')
      .prependTo($(opts.target))
      .text(text || opts.defaultText)
      .queue(function(next) {
        $(this).css({
          'opacity': 1
        });
        var topOffset = 15;
        $('.toast').each(function() {
          var $this = $(this);
          var height = $this.outerHeight();
          var offset = 15;
          $this.css('top', topOffset + 'px');

          topOffset += height + offset;
        });
        next();
      })
      .delay(opts.displayTime)
      .queue(function(next) {
        var $this = $(this);
        var width = $this.outerWidth() + 20;
        $this.css({
          'right': '-' + width + 'px',
          'opacity': 0
        });
        next();
      })
      .delay(600)
      .queue(function(next) {
        $(this).remove();
        next();
      });
  };
}

// customize it with your own options
var myOptions = {
  defaultText: 'Toast, yo!',
  displayTime: 3000,
  target: 'body'
};
  //position: 'top right',   /* TODO: make this */
  //bgColor: 'rgba(0,0,0,0.5)', /* TODO: make this */

// to get it started, instantiate a copy of
// ToastBuilder passing our custom options
var showtoast = new ToastBuilder(myOptions);



// Attach a submit handler to the form
function SubmitURL(url) {
  // Send the data using post
  var posting = $.post( '/yt/q', { url: url } );
 
  // Put the results in a div
  posting.done(function( data ) {
    if (data.success == true) {
      showtoast("Link successfully retrieved");
    }
    else {
      showtoast("Error: "+data.error);
    }
    $('#url-box').val('');
  });

  posting.error(function () {
    showtoast("Error: POST to service failed");
  });

};

// Attach a submit handler to the form
function SubmitSearch(artist, title, album) {
  // Send the data using post
  var posting = $.get( '/yt/search', { artist: artist, title: title, album:album } );
 
  // Put the results in a div
  posting.done(function( data ) {
    if (data.success == true) {
      showtoast("Link successfully retrieved");
    }
    else {
      showtoast("Error: "+data.error);
    }
    $('#search-box').val('');
  });

  posting.error(function () {
    showtoast("Error: POST to service failed");
  });

};



// wire it up
$('#url-btn').click(function() {
  SubmitURL($('#url-box').val());
});

// fires off a toast when you hit enter
$('#url-box').keypress(function(e) {
  if (e.which == 13) {
    SubmitURL($('#url-box').val());
    return false;
  }
});

// wire it up
$('#search-btn').click(function() {
  SubmitSearch( $('#artist-box').val(), $('#title-box').val(), $('#album-box').val());
});
