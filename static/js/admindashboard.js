if (typeof(Storage) !== "undefined") {
        if(localStorage.getItem("sidebar") == "opened"){
            document.getElementById("mySidenav").style.width = "250px";
            document.getElementById("main").style.marginLeft = "250px";
        }
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