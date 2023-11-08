<?php

require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Cell\Coordinate;

function readEvenColumnsFromRow($filePath) {
    $result = [];
    $file = fopen($filePath, 'r');
    $dataList = fgetcsv($file);
    while (($row = fgetcsv($file)) !== false) {
        foreach($row as $colIndex => $value) {
            $date = $dataList[$colIndex];
            $result["-{$date}-"][] = str_replace('概念', '', $value ?: '');
        }
    }

    return array_reverse($result, true);
}
$yearList = range(date('Y'), 2018);

$year = $_GET['year'] ?? $yearList[0];

$filePath = __DIR__."/resources/processed/GNBK{$year}.csv";

$data = readEvenColumnsFromRow($filePath);


?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>概念板块大势榜</title>
    <style>
        table {
            border-collapse: collapse;
            width: max-content;
        }
        td, th {
            border: 1px solid rgba(0, 0, 0, 0.23);
            width: 100px;
            text-align: center;
            cursor: pointer;
        }
        th {
            background-color: black;
            color: white;
            position: sticky;
            top: 0;
        }
        #grid-container {
            width: 100%;
            overflow-x: auto;
        }
        .fixed-links {
          margin: 10px;
        }
        .highlight {
          color: #FF5733;
          font-weight: bold;
          font-size: 20px;
          text-decoration: underline;
        }
        #tooltip {
          position: absolute;
          background-color: #fff;
          border: 1px solid #ccc;
          padding: 10px;
          font-size: 20px;
        }
        .table-empty1 {
          background-color: red;
          border-color: red;
        }
        .table-empty2 {
            background-color: #ffb700;
            border-color: #ffb700;
        }
        .table-empty3 {
            background-color: #2fff00;
            border-color: #2fff00;
        }
    </style>
</head>
<body>
    <div class="fixed-links">
        <?php foreach ($yearList as $value): ?>
            <a href="?year=<?=$value?>" <?php if ($value == $year): ?>class="highlight"<?php endif ?>><?=$value?></a>
        <?php endforeach ?>
    </div>
    <div id="grid-container">
        <table id="grid"></table>
        <div id="tooltip" style="display:none;"></div>
    </div>

    <script>
        // 提供的数据
        let data = <?=json_encode($data)?>;

        function renderGrid() {
            let table = document.getElementById('grid');
            table.innerHTML = ''; 

            var tooltip = document.getElementById('tooltip');

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

            // 以最大列长度为标准，添加数据行
            let maxRows = Math.max(...Object.values(data).map(col => col.length));
            for (let i = 0; i < maxRows; i++) {
                let row = document.createElement('tr');
                for (let colName in data) {
                    let cell = document.createElement('td');
                    row.appendChild(cell);
                    let value = data[colName][i] || "";
                    value = value.split('|');
                    cell.textContent = value[0];  // 如果超出列长度，则设置为空
                    if (cell.textContent == "") {
                        cell.classList.add("table-empty" + parseInt(i / 20));
                        continue;
                    }
                    cell.setAttribute('v', value[1]);
                    cell.addEventListener('click', function() {
                        highlightCells(cell.textContent);
                    });
                    cell.addEventListener('mouseover', function() {
                        tooltip.textContent = this.getAttribute('v');

                        // 计算tooltip的位置
                        var boundingRect = this.getBoundingClientRect();
                        var tooltipX = boundingRect.right + window.pageXOffset -10;
                        var tooltipY = boundingRect.bottom + window.pageYOffset -10;

                        tooltip.style.display = 'block';
                        tooltip.style.left = tooltipX + 'px';
                        tooltip.style.top = tooltipY + 'px';
                    });
                }
                table.appendChild(row);
            }
        }

        function getRandomColor() {
            var letters = '0123456789ABCDEF';
            var color = '#';
            for (var i = 0; i < 3; i++) {
                color += letters[Math.floor(Math.random() * 6) + 8]; // 从8到F中选择亮色
            }
            return color;
        }

        function highlightCells(value) {
            let cells = document.querySelectorAll('td');
            color = getRandomColor();
            for (let cell of cells) {
                if (cell.textContent == value) {
                    cell.style.backgroundColor = cell.style.backgroundColor ? "" : color;
                }
            }
        }

        renderGrid();

    </script>
</body>
</html>