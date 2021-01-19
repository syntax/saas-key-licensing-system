function relayUserTime(user){
    var time = new Date().getHours();
    if (0<time && time<12) {
        document.getElementById("time").innerHTML = "Good morning {0}!".format(user);
    } else if (12<time && time<17) {
        document.getElementById("time").innerHTML = "Good farhter {0}!".format(user);
    } else {
        document.getElementById("time").innerHTML = "Good cock {0}!".format(user);
    }
}