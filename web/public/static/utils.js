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

function deleteDictKey(dict, key) {
  if (key in dict) {
    delete dict[key];
  }
}

function showTooltipTrend(symbol) {
  let code = getExchangeCode(`${symbol}`);
  tooltipTrend.textContent = '';
  if (!code) {
    tooltipTrend.style.display = 'none';
    return false
  }

  let timestamp = new Date().getTime();

  let img1 = document.createElement("img");
  img1.src = `https://image2.sinajs.cn/newchart/min/n/${code}.gif?t=${timestamp}`;
  tooltipTrend.appendChild(img1);
  let img2 = document.createElement("img");
  img2.src = `https://image2.sinajs.cn/newchart/daily/n/${code}.gif?t=${timestamp}`;
  tooltipTrend.appendChild(img2);
  let img3 = document.createElement("img");
  img3.src = `https://image2.sinajs.cn/newchart/weekly/n/${code}.gif?t=${timestamp}`;
  tooltipTrend.appendChild(img3);

  tooltipTrend.style.display = 'block';

  let infoCardDiv1 = document.createElement("div");
  infoCardDiv1.classList.add('stock-info', 'card-panel', 'teal', 'z-depth-5');
  infoCardDiv1.innerHTML = "";
  tooltipTrend.prepend(infoCardDiv1);
  fetch(`/stock_info/${symbol}`)
    .then(response => response.json())
    .then(infoData => {
      if (Object.keys(infoData).length === 0) {
        infoCardDiv1.innerHTML += '<div class="card-content compact-content"><p><strong>没有股票信息数据</strong></p></div>';
        return;
      }

      infoCardDiv1.innerHTML += `
    <div class="card-content compact-content">
      <p><strong>主题投资:</strong> ${infoData['主题投资']}</p>
      <p><strong>主营业务:</strong> ${infoData['主营业务']}</p>
      <p><strong>公司亮点:</strong> ${infoData['公司亮点']}</p>
      <p><strong>行业:</strong> ${infoData['行业']}</p>
      <p><strong>概念:</strong> ${infoData['概念']}</p>
      <p><strong>地域:</strong> ${infoData['地域']}</p>
      <p><strong>风格:</strong> ${infoData['风格']}</p>
      <p><strong>流通市值:</strong> ${infoData['流通市值']}</p>
    </div>
`;
    });

  fetch(`/ths_stock_info/${symbol}`)
    .then(response => response.json())
    .then(infoData => {
      infoCardDiv1.innerHTML += `
    <div class="divider"></div>
    <div class="card-content compact-content">
      <p><strong>融资融券余额:</strong> ${infoData['融资融券余额']}</p>
      <p><strong>流通市值:</strong> ${(infoData['流通市值'] / 10**8).toFixed()}</p>
      <p><strong>公司亮点:</strong> ${infoData['公司亮点']}</p>
      <p><strong>所属概念(${infoData['所属概念数量']}):</strong> ${infoData['所属概念']}</p>
      <p><strong>所属同花顺行业:</strong> ${infoData['所属同花顺行业']}</p>
      <p><strong>主营产品名称:</strong> ${infoData['主营产品名称']}</p>
      <p><strong>地域:</strong> ${infoData['省份']} ${infoData['城市']}</p>
      <p><strong>公司网站:</strong> ${infoData['公司网站']}</p>
    </div>
`;
    })

  let infoCardDiv2 = document.createElement("div");
  infoCardDiv2.classList.add('stock-info', 'card-panel', 'teal', 'z-depth-5');
  tooltipTrend.prepend(infoCardDiv2);
  fetch(`/limited_up_info/${symbol}`)
    .then(response => response.json())
    .then(infoData => {
      if (Object.keys(infoData).length === 0) {
        infoCardDiv2.innerHTML = '<div class="card-content compact-content"><p><strong>没有股票涨停数据</strong></p></div>';
        return;
      }
      infoCardDiv2.innerHTML = `
        <div class="card-content compact-content">
        <p><strong>日期:</strong> ${infoData['date']}</p>
        <p><strong>题材:</strong> ${infoData['plates_info']?.join(' + ')}</p>
        <p><strong>涨停原因:</strong> ${infoData['reason']}</p>
        <p><strong>连板:</strong>${infoData['limited_freq']}</p>
        <p><strong>上板时间:</strong> 首${infoData['first_limit_up']} 末${infoData['last_limit_up']}</p>
        <p><strong>封单比:</strong> ${infoData['buy_lock_volume_ratio']}</p>
        <p><strong>流通市值:</strong> ${infoData['flow_capital']}亿</p>
        <p><strong>换手:</strong> ${infoData['turnover_ratio']}</p>
        <p><strong>开板次数:</strong> ${infoData['break_times']}</p>
        <p><strong>上市日期:</strong> ${infoData['listed_date']}</p>
       </div>`;
    });
}

function adjTooltipTrendPosition(cell) {
  const screenHeight = window.innerHeight;
  const isTopHalf = cell.getBoundingClientRect().top <= screenHeight / 2;
  tooltipTrend.classList.toggle('right-bottom', isTopHalf);
  tooltipTrend.classList.toggle('right-top', !isTopHalf);
}
