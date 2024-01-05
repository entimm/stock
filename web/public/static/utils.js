function getRandomColor() {
  let letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 3; i++) {
    color += letters[Math.floor(Math.random() * 10)]; // 从0到9中选择暗色
  }
  return color;
}

function getExchangeCode(symbol) {
  let exchangeCode = symbol.slice(0, 2);

  if (exchangeCode === "60" || exchangeCode === "68") {
    return `sh${symbol}`;
  } else if (exchangeCode === "00" || exchangeCode === "30") {
    return `sz${symbol}`;
  } else if (exchangeCode === "43" || exchangeCode === "83" || exchangeCode === "87") {
    return `bj${symbol}`;
  } else {
    return '';
  }
}

function getTimeStrFromTs(timestamp) {
  let date = new Date(timestamp * 1000);

  let hours = date.getHours();
  let minutes = date.getMinutes();
  let seconds = date.getSeconds();

  hours = (hours < 10) ? '0' + hours : hours;
  minutes = (minutes < 10) ? '0' + minutes : minutes;
  seconds = (seconds < 10) ? '0' + seconds : seconds;

  return hours + ':' + minutes + ':' + seconds;
}

function getDateStrFromTs(timestamp) {
  const date = new Date(timestamp * 1000);

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}
