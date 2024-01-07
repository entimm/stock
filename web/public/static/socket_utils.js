function generateRandomString(length) {
  let result = '';
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const charactersLength = characters.length;

  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }

  return result;
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

function socketEmit(symbol, date = '', time = 0) {
  if (!symbol) return;
  socket.emit('message_from_client2', {
    symbol: symbol,
    date: date,
    time: time,
    socketToken: socketToken,
  });
}
