$(document).ready(function(){
    var $input = $("#app input"),
        $appendHere = $(".tagHere"),
        oldKey = 0, newKey,
        TABKEY = 9;
    $input.focus();
    
    $input.keydown(function(e){
    
      if(e.keyCode == TABKEY) {
        if(e.preventDefault) {
          e.preventDefault();
          if($(this).val() == '' || $(this).val() == ' ') {
            return false;
          }
          addTag($(this));
        }
        return false;
      }
      
      if($(this).val() == '' && e.keyCode === 8) {
        $(".tag:last-child").remove();
      }
      
    })
    
    function addTag(element) {
      var $tag = $("<div />"), $a = $("<a href='#' />"), $span = $("<span />");
      $tag.addClass('tag');
      $('<i class="fa fa-times" aria-hidden="true"></i>').appendTo($a);
      $span.text($(element).val());
      $a.bind('click', function(){
        $(this).parent().remove();
        $(this).unbind('click');
      });
      $a.appendTo($tag);
      $span.appendTo($tag);
      $tag.appendTo($appendHere);
      $(element).val('');
    }
  });