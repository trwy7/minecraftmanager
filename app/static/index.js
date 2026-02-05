function getCookie(name) {
    let value = "; " + document.cookie;
    let parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
}

const token = getCookie("token");
if (token) {
    var socket = io({
        withCredentials: true,
        auth: { token: token }
    });
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });
}