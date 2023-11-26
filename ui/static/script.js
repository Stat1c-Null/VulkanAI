//Request to call python functions
let xhr = null;
getXmlHttpRequestObject = function () {
    if (!xhr) {
        // Create a new XMLHttpRequest object
        xhr = new XMLHttpRequest();
    }
    return xhr;
};
//Hide loader after page has loaded
function hideLoader() {
    document.getElementById('loader').style.visibility = 'hidden';
}
//Show loading animation after searching and while page is loading
showLoader = function(e) {
    e.preventDefault();
    document.getElementById('loader').style.visibility = 'show';
}

//Non Production Kostyl
function wait(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

//Move user search result page
function sendToNewPage() {
    console.log("Sending user to new page");
    wait(5000);//Wait a little before rendering page
    window.location.href = "http://127.0.0.1:8000/views/search-result";
    // Check response is ready or not
    if (xhr.status == 201) {//xhr.readyState == 4 && xhr.status == 201

        window.location.href = "http://127.0.0.1:8000/views/search-result";
    }
}

document.getElementById("search-button").addEventListener("click", function(event) {
    xhr = null;
    event.preventDefault();

    let inputValue = document.getElementById("search-input").value;//If using input field use 'document.getElementById("search-input")[0].value'
    console.log(inputValue);

    xhr = getXmlHttpRequestObject();
    xhr.open("POST", "http://127.0.0.1:8000/views/search-result", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    // Send the request over the network
    xhr.send(JSON.stringify({"data": inputValue}));
    xhr.onreadystatechange = sendToNewPage();
});

//Make search bar grow in height as user keeps typing into it
var span = $('<span>').css('display','inline-block')
                      .css('word-break','break-all')
                      .appendTo('body').css('visibility','hidden');
function initSpan(textarea){
  span.text(textarea.text())
      .width("0")
      .css('font',textarea.css('font'));
}

$('textarea').on({
    input: function(){
       var text = $(this).val();
       span.text(text);
       $(this).height('1.1em');
        //Expand bar to its full height if needed
       //$(this).height(text ? span.height() : '1.1em');
    },
    focus: function(){
        var text = $(this).val();
       initSpan($(this));
       //Make search bar small if there is nothing in it
       if(text.length === 0) console.log("empty");
    },
    keypress: function(e){
       //cancel the Enter keystroke, otherwise a new line will be created
       if(e.which == 13) e.preventDefault();
    }
});

