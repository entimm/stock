    initSocket();

    document.addEventListener('keydown', function (event) {
      if (event.code === 'ArrowUp' || event.code === 'ArrowDown') {
        sendSocket(event.code);
        event.preventDefault();
      }
    });

    function processMove(direction) {
      let row = getAdjacentCell(selectedRow, direction);
      if (row) {
        setSelectedRow(row);
      }

      return row;
    }

    function setSelectedRow(row) {
      if (selectedRow) {
        selectedRow.classList.remove('select-row');
      }
      selectedRow = row;
      row.classList.add('select-row');
    }

    function getRowIndex(row) {
      return Array.from(row.parentElement.children).indexOf(row);
    }

    function getAdjacentCell(row, direction) {
      if (!row) {
        row = table.querySelector('tbody tr');
      }
      let rowIndex = getRowIndex(row);
      let numRows = table.querySelector('tbody').childNodes.length;
      switch (direction) {
        case "ArrowUp":
          return rowIndex > 0 ? table.querySelector(`tbody tr:nth-child(${rowIndex})`) : null;
        case "ArrowDown":
          return rowIndex < numRows - 1 ? table.querySelector(`tbody tr:nth-child(${rowIndex + 2})`) : null;
        default:
          return null;
      }
    }
