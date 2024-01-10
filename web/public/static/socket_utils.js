let socket = null;
let selectedRow = null;

function initSocket() {
  if (socketToken) {
    socket = io.connect(`http://${document.domain}:${location.port}`);
    socket.on('message_from_client1', function (message) {
      if (message.socketToken !== socketToken) return;
      sendSocket(message.key);
    });
  }
}

function generateRandomString(length) {
  let result = '';
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const charactersLength = characters.length;

  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }

  return result;
}

function sendSocket(direction) {
  let row = processMove(direction);
  if (row) {
    let klineParams = getKlineParams(row);
    socketEmit(klineParams.symbol, klineParams.date, klineParams.time, klineParams.price);
  }
}

function openRelateKlineMode() {
  if (socketToken) {
    window.open(`/chart?symbol=999999&period=D&socket_token=${socketToken}`, "_blank");
    return;
  }

  socketToken = generateRandomString(6);
  let currentUrl = new URL(window.location.href);
  let searchParams = currentUrl.searchParams;
  searchParams.set("socket_token", socketToken);

  history.pushState({}, '', currentUrl.toString());
  window.location.href = currentUrl.toString();
}

function socketEmit(symbol, date = '', time = 0, price = 0) {
  if (!socket) return;
  if (!symbol) return;
  socket.emit('message_from_client2', {
    symbol: symbol,
    date: date,
    time: time,
    price: price,
    socketToken: socketToken,
  });
}
