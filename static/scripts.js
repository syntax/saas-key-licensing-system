function relayUserTime(user){
    var time = new Date().getHours();
    if (0<=time && time<12) {
        document.getElementById("time").innerHTML = "Good morning " + user + " !" ;
    } else if (12<= time && time<17) {
        document.getElementById("time").innerHTML = "Good afternoon " + user + " !" ;
    } else {
        document.getElementById("time").innerHTML = "Good evening " + user + " !" ;
    }
}

function unbind() {
    $.get('/unbindaccount');
    setTimeout(function(){ location.reload(); }, 100);
}

function redirectFunct() {
   location.replace("http://127.0.0.1:5000/login")
   }

function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
  if (typeof(Storage) !== "undefined") {
        localStorage.setItem("sidebar", "opened");
    }
}
function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
  if (typeof(Storage) !== "undefined") {
        localStorage.setItem("sidebar", "closed");
    }
}
