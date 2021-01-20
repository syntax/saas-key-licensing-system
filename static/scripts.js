function relayUserTime(user){
    var time = new Date().getHours();
    if (0<time && time<12) {
        document.getElementById("time").innerHTML = "Good morning" + user + "!" ;
    } else if (12<time && time<17) {
        document.getElementById("time").innerHTML = "Good afternoon" + user + "!" ;
    } else {
        document.getElementById("time").innerHTML = "Good evening" + user + "!" ;
    }
}