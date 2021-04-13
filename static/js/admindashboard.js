// following selections set sidebar to be open or closed in correspodnging with localstorage (from last page visited)

if (typeof(Storage) !== "undefined") {
        if(localStorage.getItem("sidebar") == "opened"){
            document.getElementById("mySidenav").style.width = "250px";
            document.getElementById("main").style.marginLeft = "250px";
        }
    }
function openNav() {
  // function for opening navigation panel, commits to local storage after change
  document.getElementById("mySidenav").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
  if (typeof(Storage) !== "undefined") {
        localStorage.setItem("sidebar", "opened");
    }
}
function closeNav() {
  // function for closing navigation panel, commits to local storage after it has been changed
  document.getElementById("mySidenav").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
  if (typeof(Storage) !== "undefined") {
        localStorage.setItem("sidebar", "closed");
    }
}