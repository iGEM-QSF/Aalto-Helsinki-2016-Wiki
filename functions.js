<script>

$(window).scroll(function(){
	$(".title").css("opacity", 1 - $(window).scrollTop() / 500);
});

</script>
	
	<script>
	$(document).ready(function () {
    $(window).scroll(function () {
        var s = $(document).scrollTop(),
            d = $(document).height() - $(window).height();          
        $("#progressbar").attr('max', d);
        $("#progressbar").attr('value', s);
     });
 });
	
	</script>

	<script>
    var h1s = document.getElementsByTagName("h1");
    for (var i = 0; i < h1s.length; i++) {
        var h1 = h1s[i];
        $( "<li><a href=\"#"+ h1.id +"\">" + h1.textContent + "</a></li>" ).appendTo( ".botnav" );
        console.log(h1);
    }
    </script>

    <script>
    $(function() {
    $('a[href*="#"]:not([href="#"])').click(function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
      if (target.length) {
        $('html, body').animate({
          scrollTop: target.offset().top - 50
        }, 1000);
        return false;
      }
    }
  });
});

    </script>
	
	<script> 
	var links = $('ul.botnav li a');
	var h1s = $("h1");
	var alreadyFound = 0;
	
	$(window).scroll(function() {
	for (var i = links.length-1; i >= 0; i--) {
		
		if ($(this).scrollTop() > $(h1s[i]).offset().top - 70 && alreadyFound == 0) {
		console.log('hei');
        $(links[i]).addClass("active");
		alreadyFound = 1;
		} 
		else {
		$(links[i]).removeClass("active");
		}
	
	}
	alreadyFound = 0;
	});	
	
    </script>