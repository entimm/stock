<?php

require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Cell\Coordinate;

function readEvenColumnsFromRow($filePath) {
    $spreadsheet = IOFactory::load($filePath);
    $worksheet = $spreadsheet->getActiveSheet();
    $highestColumn = $worksheet->getHighestColumn();
    $highestColumnIndex = Coordinate::columnIndexFromString($highestColumn);

    $result = [];

    for ($i = 1; $i <= $highestColumnIndex; $i += 1) {
        $date = $worksheet->getCellByColumnAndRow($i, 1)->getValue();

        foreach (range(2, 101) as $index => $rowNumber) {
            $value = $worksheet->getCellByColumnAndRow($i, $rowNumber)->getValue();
            $result["-{$date}-"][] = $value ?: '';
        }
    }

    return array_reverse($result, true);
}

$maList = [
    'ma5',
    'ma10',
    'ma20',
    'ma60',
];
$yearList = range(date('Y'), 2011);

$ma = $_GET['ma'] ?? $maList[0];
$year = $_GET['year'] ?? $yearList[0];

$filePath = __DIR__."/resources/processed/{$year}-{$ma}-asc.xlsx";

$data = readEvenColumnsFromRow($filePath);


?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个股趋势涨幅榜</title>
    <style>
        table {
            border-collapse: collapse;
            width: max-content;
        }
        td, th {
            border: 1px solid black;
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
            height: 100vh;
            overflow-x: auto;
            overflow-y: auto;
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
    </style>
</head>
<body>
    <div class="fixed-links">
        <?php foreach ($maList as $value): ?>
            <a href="?ma=<?=$value?>&year=<?=$year?>" <?php if ($value == $ma): ?>class="highlight"<?php endif ?>><?=$value?></a>
        <?php endforeach ?>
    </div>
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
                    let value = data[colName][i] || "";
                    value = value.split('|');
                    cell.textContent = value[0];  // 如果超出列长度，则设置为空
                    cell.setAttribute('v', value[1]);
                    if (cell.textContent == "") cell.style.backgroundColor = "#8D4004";
                    cell.addEventListener('click', function() {
                        highlightCells(cell.textContent);
                    });
                    cell.addEventListener('mouseover', function() {
                        var myValue = this.getAttribute('v');
                        tooltip.textContent = myValue;
                        tooltip.style.display = 'block';
                        tooltip.style.left = event.clientX + 'px';
                        tooltip.style.top = event.clientY + 'px';
                    });
                    row.appendChild(cell);
                }
                table.appendChild(row);
            }
        }

        function getRandomColor() {
            // 生成随机的红、绿、蓝色值
            let r = Math.floor(Math.random() * 256);
            let g = Math.floor(Math.random() * 256);
            let b = Math.floor(Math.random() * 256);

            // 将RGB值转换成十六进制，并拼接成颜色值
            let hexColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
            
            return hexColor;
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