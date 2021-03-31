function redirectFunct() {
    location.replace("http://127.0.0.1:5000/login")
}

setTimeout(function(){ redirectFunct(); }, 3000);