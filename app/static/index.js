function getCookie(name) {
    let value = "; " + document.cookie;
    let parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
}

const token = getCookie("token");
var socket = io({
    auth: { token: token }
});
let cdc = false;
socket.on("connect", () => {
    console.log("Connected to server");
    if (cdc) {
        // sloppy way of doing it, should probably just re-request the status of all servers
        location.reload();
    }
    document.getElementById("header-center").innerText = "Connected";
    document.getElementById("header-center").style.color = "rgb(147, 255, 147)";
});
socket.on("disconnect", () => {
    console.log("Disconnected from server");
    cdc = true;
    document.getElementById("header-center").innerText = "Disconnected";
    document.getElementById("header-center").style.color = "#e35252";
});
window.addEventListener('pageshow', function(event) {
    // why is this not simpler
    if (event.persisted) {
        window.location.reload();
    }
});