let selectedCell = null;
let focusMode = 'cursor';
let tooltipTrend = document.getElementById('tooltip-trend');
let tooltip = document.getElementById('tooltip');
let iframe = document.getElementById('iframeContent');
let table = document.getElementById('grid');
window.addEventListener('message', function (event) {
  if (event.data === 'close_me') {
    closeDialog();
  }
  if (['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp'].includes(event.data)) {
    let cell = getAdjacentCell(selectedCell, event.data)
    if (cell) {
      let symbol = cell.getAttribute('symbol');
      if (symbol) {
        iframe.src = iframe.contentWindow.document.URL.replace(/\d{6}/, symbol);
        setSelectedCell(cell);
      }
    }
  }
});

document.addEventListener('keydown', function (event) {
  if (event.code === 'ArrowUp' || event.code === 'ArrowDown' || event.code === 'ArrowLeft' || event.code === 'ArrowRight') {
    let cell = getAdjacentCell(selectedCell, event.code)
    if (cell) {
      focusMode = 'key'
      setSelectedCell(cell);
      show_tooltip(cell);
      show_tooltip_trend(cell);
    }
    return;
  }
  if (event.code === 'Space') {
    if (selectedCell) {
      let symbol = selectedCell.getAttribute('symbol');
      if (symbol) {
        openDialog(`/chart?symbol=${symbol}&period=F5`);
      }
    }
    return;
  }
  if (event.code === 'Escape') {
    tooltip.style.display = 'none';
    tooltipTrend.style.display = 'none';
    focusMode = 'key'
  }
});

function renderGrid(data) {
  table.innerHTML = '';

  // 添加表头
  let thead = document.createElement('thead');
  let headerRow = document.createElement('tr');
  for (let colName in data) {
    let headerCell = document.createElement('th');
    headerCell.textContent = colName;
    headerRow.appendChild(headerCell);
  }
  thead.appendChild(headerRow);
  table.appendChild(thead);

  let tbody = document.createElement('tbody');

  // 以最大列长度为标准，添加数据行
  let maxRows = Math.max(...Object.values(data).map(col => col.length));
  for (let i = 0; i < maxRows; i++) {
    let row = document.createElement('tr');
    for (let colName in data) {
      let cell = document.createElement('td');
      row.appendChild(cell);
      renderCell(cell, data[colName][i] || "", i)
    }
    tbody.appendChild(row);
  }
  table.appendChild(tbody);
}

function renderCell(cell, value, i) {
  value = value.split('|');
  cell.textContent = value[0];
  if (cell.textContent === "") {
    cell.classList.add("table-empty" + parseInt(i / 20));
    return;
  }
  addDotClass(cell, value)
  cell.setAttribute('v', value.slice(2).join(' # '));
  cell.setAttribute('symbol', value[1]);
  cell.addEventListener('click', function () {
    let cellRect = cell.getBoundingClientRect();

    let clickX = event.clientX - cellRect.left;

    if (clickX < cellRect.width / 2) {
      highlightCells(cell.textContent);
    } else {
      setSelectedCell(cell);
      if (focusMode === 'cursor') {
        openDialog(`/chart?symbol=${value[1]}&period=${KLINE_PERIOD}`);
      }
      if (tooltipTrend.style.display === 'none') {
        show_tooltip_trend(cell);
        show_tooltip(cell);
      }
      focusMode = 'cursor';
    }
  });
  cell.addEventListener('mouseover', function () {
    if (focusMode === 'cursor') {
      show_tooltip_trend(this);
      show_tooltip(this);
      setSelectedCell(this);
    }

  });
}

function openDialog(url) {
  iframe.src = url;

  chartDialog.showModal();

  document.addEventListener('click', handleClickOutside);
}

function closeDialog() {
  chartDialog.close();
  document.removeEventListener('click', handleClickOutside);
}

function handleClickOutside(event) {
  if (event.target === chartDialog) {
    closeDialog();
  }
}

function getAdjacentCell(cell, direction) {
  if (!cell) return;
  let row = cell.parentNode.rowIndex;
  let col = cell.cellIndex;

  let numRows = table.rows.length;
  let numCols = table.rows[0].cells.length;

  switch (direction) {
    case "ArrowUp":
      return row > 0 ? table.rows[row - 1].cells[col] : null;
    case "ArrowRight":
      return col < numCols - 1 ? table.rows[row].cells[col + 1] : null;
    case "ArrowDown":
      return row < numRows - 1 ? table.rows[row + 1].cells[col] : null;
    case "ArrowLeft":
      return col > 0 ? table.rows[row].cells[col - 1] : null;
    default:
      return null;
  }
}

function setSelectedCell(cell) {
  if (selectedCell) {
    selectedCell.classList.remove('select-cell')
  }
  selectedCell = cell
  cell.classList.add('select-cell')
}

function getRandomColor() {
  let letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 3; i++) {
    color += letters[Math.floor(Math.random() * 6) + 8]; // 从8到F中选择亮色
  }
  return color;
}

function highlightCells(value) {
  let cells = document.querySelectorAll('td');
  color = getRandomColor();
  for (let cell of cells) {
    if (cell.textContent === value) {
      cell.style.backgroundColor = cell.style.backgroundColor ? "" : color;
    }
  }
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

function show_tooltip_trend(cell) {
  let symbol = cell.getAttribute('symbol') ?? '';
  let code = getExchangeCode(symbol);
  tooltipTrend.textContent = '';
  if (!code) {
    tooltipTrend.style.display = 'none';
    return
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

  // 计算tooltipTrend的位置
  let screenHeight = window.innerHeight;
  const isTopHalf = cell.getBoundingClientRect().top <= screenHeight / 2;
  tooltipTrend.classList.toggle('right-bottom', isTopHalf);
  tooltipTrend.classList.toggle('right-top', !isTopHalf);

  tooltipTrend.style.display = 'block';

  let infoCardDiv = document.createElement("div");
  infoCardDiv.classList.add('stock-info', 'card-panel', 'teal');
  tooltipTrend.prepend(infoCardDiv);
  fetch(`/stock_info/${symbol}`).then(response => response.json())
    .then(jsonData => {
      infoCardDiv.innerHTML = `
        <div class="card-content compact-content">
            <p><strong>主题投资:</strong> ${jsonData['主题投资']}</p>
            <p><strong>主营业务:</strong> ${jsonData['主营业务']}</p>
            <p><strong>公司亮点:</strong> ${jsonData['公司亮点']}</p>
            <p><strong>行业:</strong> ${jsonData['行业']}</p>
            <p><strong>概念:</strong> ${jsonData['概念']}</p>
            <p><strong>地域:</strong> ${jsonData['地域']}</p>
            <p><strong>风格:</strong> ${jsonData['风格']}</p>
            <p><strong>流通市值:</strong> ${jsonData['流通市值']}</p>
        </div>
    `;
    });
}

function show_tooltip(cell) {
  tooltip.textContent = cell.getAttribute('v');

  // 计算tooltip的位置
  let boundingRect = cell.getBoundingClientRect();
  let tooltipX = boundingRect.right + window.pageXOffset - 10;
  let tooltipY = boundingRect.bottom + window.pageYOffset - 10;

  tooltip.style.display = 'block';
  tooltip.style.left = tooltipX + 'px';
  tooltip.style.top = tooltipY + 'px';
}