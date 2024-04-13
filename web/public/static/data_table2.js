let selectedCell = null;
let showDaily = false;
let focusMode = 'cursor';
let tooltipTrend = document.getElementById('tooltip-trend2');
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
      let headName = getCellHeadName(cell);
      let date = /^\d{4}-\d{2}-\d{2}$/.test(headName) ? headName : '';
      if (symbol) {
        iframe.src = iframe.contentWindow.document.URL.replace(/\d{6}/, symbol).replace(/\d{4}-\d{2}-\d{2}/, date);
        setSelectedCell(cell);
      }
    }
  }
});

document.addEventListener('keydown', function (event) {
  if (event.code === 'ArrowUp' || event.code === 'ArrowDown' || event.code === 'ArrowLeft' || event.code === 'ArrowRight') {
    let cell = processMove(event.code);
    if (!cell) return;
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
  container.style.maxHeight = (maxRows + 1) * 25 + 'px'; // 设置最大高度，根据实际情况调整
  container.style.position = 'relative';

  thead.addEventListener('click', function (event) {
    if (event.target.tagName === 'TH') {
      showTooltipTrend(event.target);
      focusMode = 'key';
      setSelectedCell(event.target);
    }
  });

  tbody.addEventListener('click', function (event) {
    if (event.target.tagName === 'TD') {
      let cell = event.target;
      let cellRect = cell.getBoundingClientRect();

      let clickX = event.clientX - cellRect.left;

      if (clickX < cellRect.width / 2) {
        highlightCells(cell.getAttribute('symbol'));
      } else {
        let symbol = cell.getAttribute('symbol');
        if (!symbol) return;

        let headName = getCellHeadName(cell);

        setSelectedCell(cell);
        show_tooltip(cell);
        showTooltipTrend(cell);

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
  showTooltipTrend(cell)
}, 200);

function renderCell(cell, value, i) {
  if (!value) return;
  value = value.split('|');
  let symbol = value[1];
  let is20cm = ['30', '68'].includes(symbol?.slice(0, 2));
  cell.innerHTML = is20cm ? (`@${value[0]}`) : value[0];
  if (value[2] === 'ZT') {
    cell.innerHTML += `<sub>${value[3]}</sub>`;
  }
  if (cell.textContent === "") {
    cell.classList.add("table-empty" + parseInt(i / 20));
    return;
  }
  addDotClass(cell, value)
  cell.setAttribute('v', value.slice(2).join(' # '));
  cell.setAttribute('symbol', symbol);
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
  let rowIndex = getRowIndex(cell);
  let colIndex = cell.cellIndex;

  let numRows = table.querySelector('tbody').childNodes.length;
  let numCols = table.querySelector('thead tr').cells.length;

  switch (direction) {
    case "ArrowUp":
      return rowIndex > 0 ? table.querySelector(`tbody tr:nth-child(${rowIndex}) td:nth-child(${colIndex + 1})`) : null;
    case "ArrowRight":
      return colIndex < numCols - 1 ? cell.nextElementSibling : null;
    case "ArrowDown":
      return rowIndex < numRows - 1 ? table.querySelector(`tbody tr:nth-child(${rowIndex + 2}) td:nth-child(${colIndex + 1})`) : null;
    case "ArrowLeft":
      return colIndex > 0 ? cell.previousElementSibling : null;
    default:
      return null;
  }
}

function getCellHeadName(cell) {
  let col = cell.cellIndex;

  return table.querySelector('thead tr').cells[col].innerHTML;
}

function getNextCellHeadName(cell, n = 1) {
  let col = cell.cellIndex;

  return table.querySelector('thead tr').cells[col - n]?.innerHTML;
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
    if (cell.getAttribute('symbol') === value) {
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

function processMove(direction) {
  let cell = getAdjacentCell(selectedCell, direction);
  if (cell) {
    focusMode = 'key';
    setSelectedCell(cell);
    show_tooltip(cell);
    showTooltipTrend(cell);
  }

  return cell;
}

function showTooltipTrend(cell) {
  let date = getCellHeadName(cell);
  let nextDate = getNextCellHeadName(cell);
  let next2Date = getNextCellHeadName(cell, 2);
  let next3Date = getNextCellHeadName(cell, 3);

  let symbolList = [];
  if (cell.getAttribute('symbol')) {
    symbolList = [cell.getAttribute('symbol')];
  } else if (cell.tagName === 'TH') {
    symbolList = data[date].map(function (item) {
      let values = item.split('|');
      return values[1];
    });
  } else {
    return;
  }

  tooltipTrend.textContent = '';

  if (symbolList.length === 1) {
    let symbol = symbolList[0];

    [next3Date, next2Date, nextDate, date].forEach(function (param) {
      let img = document.createElement("img");
      img.src = `http://${document.domain}:${location.port}/static/imgs/min/${param}/${symbol}.gif`;
      let a = document.createElement("a");
      a.href = `http://${document.domain}:${location.port}/chart?date=${param}&period=D&symbol=${symbol}`
      a.target = 'blank';
      a.appendChild(img);
      tooltipTrend.appendChild(a);
    })

    let img2 = document.createElement("img");
    img2.src = `http://${document.domain}:${location.port}/static/imgs/daily/${date}/${symbol}.gif`;
    let a2 = document.createElement("a");
    a2.href = `http://${document.domain}:${location.port}/chart?date=${date}&period=F5&symbol=${symbol}`
    a2.target = 'blank';
    a2.appendChild(img2);
    tooltipTrend.appendChild(a2);

    adjTooltipTrendPosition(tooltipTrend, cell);
    tooltipTrend.style.display = 'block';
    return;
  }

  for (symbol of symbolList) {
    let img = document.createElement("img");

    img.src = `http://${document.domain}:${location.port}/static/imgs/${showDaily ? 'daily' : 'min'}/${date}/${symbol}.gif`;
    let a = document.createElement("a");
    a.href = `http://${document.domain}:${location.port}/chart?date=${date}&period=${showDaily ? 'D' : 'F5'}&symbol=${symbol}`
    a.target = 'blank';
    a.appendChild(img);
    tooltipTrend.appendChild(a);
  }
  adjTooltipTrendPosition(tooltipTrend, cell);
  tooltipTrend.style.display = 'block';
}
