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
    let cell = getAdjacentCell(selectedCell, event.data);
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
    let cell = processMove(event.code);
    let headName = getCellHeadName(cell);
    let date = /^\d{4}-\d{2}-\d{2}$/.test(headName) ? headName : '';
    let symbol = cell.getAttribute('symbol');
    if (symbol && socket) {
      openDialog(symbol, date);
    }
    event.preventDefault();
    return;
  }
  if (event.code === 'Space') {
    if (selectedCell) {
      let headName = getCellHeadName(selectedCell);
      let date = /^\d{4}-\d{2}-\d{2}$/.test(headName) ? headName : '';
      let symbol = selectedCell.getAttribute('symbol');
      if (symbol) {
        openDialog(symbol, date, true);
      }
    }
    event.preventDefault();
    return;
  }
  if (event.code === 'Escape') {
    tooltip.style.display = 'none';
    tooltipTrend.style.display = 'none';
    focusMode = 'cursor'
  }
});

function renderGrid(data) {
  table.innerHTML = '';

  let container = document.createElement('div');
  container.classList.add('table-container');
  container.id = 'table-container'

  let thead = document.createElement('thead');
  let headerRow = document.createElement('tr');
  for (let colName in data) {
    let headerCell = document.createElement('th');
    headerCell.textContent = colName;
    headerRow.appendChild(headerCell);
  }
  thead.appendChild(headerRow);

  let tbody = document.createElement('tbody');

  let maxRows = Math.max(...Object.values(data).map(col => col.length));
  for (let i = 0; i < maxRows; i++) {
    let row = document.createElement('tr');
    for (let colName in data) {
      let cell = document.createElement('td');
      row.appendChild(cell);
      renderCell(cell, data[colName][i] || "", i);
    }
    tbody.appendChild(row);
  }

  container.appendChild(thead);
  container.appendChild(tbody);
  table.appendChild(container);

  container.addEventListener('scroll', function () {
    thead.style.transform = `translateX(-${container.scrollLeft}px)`;
  });

  container.style.overflowX = 'auto';
  container.style.overflowY = 'hidden';
  container.style.maxHeight = maxRows * 25 + 'px'; // 设置最大高度，根据实际情况调整
  container.style.position = 'relative';

  thead.addEventListener('click', function (event) {
    if (event.target.tagName === 'TH') {
      let colName = event.target.textContent;
      let symbols = data[colName].slice(0, 20).map(function (item) {
        let values = item.split('|');
        return values[1];
      }).join('-');
      if (/^\d{4}-\d{2}-\d{2}$/.test(colName)) {
        window.open(`/line2?date=${colName}&period=D&flag=1&symbols=${symbols}`, "_blank");
      }
    }
  });

  tbody.addEventListener('click', function (event) {
    if (event.target.tagName === 'TD') {
      let cell = event.target;
      let cellRect = cell.getBoundingClientRect();

      let clickX = event.clientX - cellRect.left;

      if (clickX < cellRect.width / 2) {
        highlightCells(cell.textContent);
      } else {
        let symbol = cell.getAttribute('symbol');
        if (!symbol) return;

        setSelectedCell(cell);
        show_tooltip_trend(cell);
        show_tooltip(cell);

        let headName = getCellHeadName(cell);
        let date = /^\d{4}-\d{2}-\d{2}$/.test(headName) ? headName : '';
        openDialog(symbol, date);

        focusMode = 'key';
      }
    }
  });
  tbody.addEventListener('mouseover', function (event) {
    if (event.target.tagName === 'TD') {
      let cell = event.target;
      if (focusMode === 'cursor') {
        debouncedFunction(cell);
        show_tooltip(cell);
        setSelectedCell(cell);
      }
    }
  });
}

function debounce(func, delay) {
  let timeoutId;

  return function () {
    clearTimeout(timeoutId);

    timeoutId = setTimeout(() => {
      func.apply(this, arguments);
    }, delay);
  };
}

const debouncedFunction = debounce(function (cell) {
  show_tooltip_trend(cell);
}, 200);

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
}

function openDialog(symbol = '', date = '', useDialog = false) {
  if (!useDialog && socket && symbol) {
    socketEmit(symbol, date);
    return;
  }

  iframe.src = `/chart?symbol=${symbol}&period=${KLINE_PERIOD}&date=${date}`;
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

function getRowIndex(cell) {
  let row = cell.parentElement;
  return Array.from(row.parentElement.children).indexOf(row);
}

function getAdjacentCell(cell, direction) {
  if (!cell) {
    cell = table.querySelector('tbody tr').cells[0];
  }
  let row = getRowIndex(cell);
  let col = cell.cellIndex;

  let numRows = table.querySelector('tbody').childNodes.length;
  let numCols = table.querySelector('thead tr').cells.length;

  switch (direction) {
    case "ArrowUp":
      return row > 0 ? table.querySelector(`tbody tr:nth-child(${row}) td:nth-child(${col + 1})`) : null;
    case "ArrowRight":
      return col < numCols - 1 ? cell.nextElementSibling : null;
    case "ArrowDown":
      return row < numRows - 1 ? table.querySelector(`tbody tr:nth-child(${row + 2}) td:nth-child(${col + 1})`) : null;
    case "ArrowLeft":
      return col > 0 ? cell.previousElementSibling : null;
    default:
      return null;
  }
}

function getCellHeadName(cell) {
  let col = cell.cellIndex;

  return table.querySelector('thead tr').cells[col].innerHTML;
}

function setSelectedCell(cell) {
  if (selectedCell) {
    selectedCell.classList.remove('select-cell')
  }
  selectedCell = cell
  cell.classList.add('select-cell')
}

function highlightCells(value) {
  let cells = document.querySelectorAll('td');
  color = getRandomColor();
  for (let cell of cells) {
    if (cell.textContent === value) {
      if (cell.style.backgroundColor) {
        cell.style.backgroundColor = "";
        cell.style.color = '#000';
      } else {
        cell.style.backgroundColor = color;
        cell.style.color = '#fff';
      }
    }
  }
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
  infoCardDiv.classList.add('stock-info', 'card-panel', 'teal', 'z-depth-5');
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
    </div>`;
    });

  let infoCardDiv2 = document.createElement("div");
  infoCardDiv2.classList.add('stock-info', 'card-panel', 'teal', 'z-depth-5');
  tooltipTrend.prepend(infoCardDiv2);
  fetch(`/limited_up_info/${symbol}`).then(response => response.json())
    .then(jsonData => {
      infoCardDiv2.innerHTML = `
        <div class="card-content compact-content">
        <p><strong>日期:</strong> ${jsonData['date']}</p>
        <p><strong>题材:</strong> ${jsonData['plates_info']?.join(' + ')}</p>
        <p><strong>涨停原因:</strong> ${jsonData['reason']}</p>
        <p><strong>连板:</strong>${jsonData['limited_freq']}</p>
        <p><strong>上板时间:</strong> 首${jsonData['first_limit_up']} 末${jsonData['last_limit_up']}</p>
        <p><strong>封单比:</strong> ${jsonData['buy_lock_volume_ratio']}</p>
        <p><strong>流通市值:</strong> ${jsonData['flow_capital']}亿</p>
        <p><strong>换手:</strong> ${jsonData['turnover_ratio']}</p>
        <p><strong>开板次数:</strong> ${jsonData['break_times']}</p>
        <p><strong>上市日期:</strong> ${jsonData['listed_date']}</p>
       </div>`;
    });
}

function processMove(direction) {
  let cell = getAdjacentCell(selectedCell, direction);
  if (cell) {
    focusMode = 'key';
    setSelectedCell(cell);
    show_tooltip(cell);
    show_tooltip_trend(cell);
  }

  return cell;
}
