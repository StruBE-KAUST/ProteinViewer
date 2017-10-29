/*
Calls check every second, which sends a get request to check.py and reloads the page
when the subprocess running load.py is complete (when check returns success or fail states)
*/

FAILED_STATE = -1
SUCCESS_STATE = 1

$(function(){
	// runs every second
  setInterval(check, 1000)
});  

function check(){
	$.ajax({
	  async: true,
	  type: 'GET',
	  url: "check/"
	}).done(function(data){
		if(data == SUCCESS_STATE || data == FAILED_STATE){
			// the subprocess is complete; reload the page
			// when this reloads, it calls intermediate.py, which decides if viewer.html is loaded or if the form is loaded again
			location.reload(true);
		}
	});
}