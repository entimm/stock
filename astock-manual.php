<?php

require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Cell\Coordinate;


function readEvenColumnsFromRow($filePath, $rowNumbers, $worksheetName) {
    $spreadsheet = IOFactory::load($filePath);
    $worksheet = $spreadsheet->getSheetByName($worksheetName);
    $highestColumn = $worksheet->getHighestColumn();
    $highestColumnIndex = Coordinate::columnIndexFromString($highestColumn);

    $result = [];

    // 循环偶数列
    for ($i = 2; $i <= $highestColumnIndex; $i += 2) {
        $date = $worksheet->getCellByColumnAndRow($i - 1, 1)->getValue();

        foreach ($rowNumbers as $rowNumber) {
            $value = 0;
            $j = 1;
            while (!($value = (int)$worksheet->getCellByColumnAndRow($i, $rowNumber + $j)->getValue()) && $j < 10) {
                $j++;
            }

            if ($value) {
              $result['name'][$date][] = $worksheet->getCellByColumnAndRow($i - 1, $rowNumber + $j)->getValue();
              $result['value'][$date][] = $value;
            }
        }
    }

    return $result;
}

$worksheets = [
    '5日',
    '10日',
    '20日',
    '60日',
    '近年3月',
];

$filePath = '/Users/enjoy/Library/CloudStorage/OneDrive-Personal/Docments/牛股每日榜单.xlsx';

$rows = [1, 2, 3, 4, 5, 10, 20,30, 40];

$worksheetId = $_GET['worksheet_id'] ?? 0;
$worksheetName = $worksheets[$worksheetId];

$data = readEvenColumnsFromRow($filePath, $rows, $worksheetName);
?>

<!DOCTYPE html>
<html>
<head>
  <title>A股龙头趋势图 - <?=$worksheetName?></title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.1.2/dist/echarts.min.js"></script>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      height: 100%;
    }

    #densityChart {
      width: 100%;
      height: 100%;
    }

    .fixed-links {
      position: fixed;
      top: 0;
      right: 0;
      margin: 20px 40px;
      z-index: 9999; 
    }

    .highlight {
      color: #FF5733;
      font-weight: bold;
      font-size: 20px;
      text-decoration: underline;
    }
  </style>
</head>
<body>
    <div class="fixed-links">
        <?php foreach ($worksheets as $key => $value): ?>
            <a href="?worksheet_id=<?=$key?>" <?php if ($key == $worksheetId): ?>class="highlight"<?php endif ?>><?=$value?></a>
        <?php endforeach ?>
    </div>
    <div style="clear: both;"></div>

  <div id="densityChart"></div>

  <script>
    var rows = <?=json_encode($rows)?>;
    rows = rows.map(v => "NO."+v);
    var dataName = <?=json_encode($data['name'])?>;
    var dataValue = <?=json_encode($data['value'])?>;

    // 创建数据密度图的配置
    var chartConfig = {
      color: [
        "#FF33EC",
        "#FF5733",
        "#3357FF",
        "#00FFFF",
        "#008000",
        "#FFA500",
        "#33FF57",
        "#808080",
        "#2F80ED",
        "#EB5757",
        "#27AE60",
        "#F2994A",
        "#9B51E0",
        "#A0522D",
        "#2D9CDB",
        "#FF6B81",
        "#00A8FF",
        "#00D8D0",
      ],
      legend: {
        data: rows
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: Object.keys(dataValue) // 使用年份和月份组合作为x轴数据
      },
      yAxis: {
        type: 'value',
        interval: 50,
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 9999
        },
        {
          start: 0,
          end: 9999
        }
      ],
      grid: {
        left: '1%',
        right: '1%',
        containLabel: true
      },
      series: [],
      tooltip: {
        stack: 'Total',
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: function (params) {
            return params.map(
              item => (item.marker + '<span style="display:inline-block;width:60px">' + item.seriesName  + '</span>' + '<span style="display:inline-block;width:40px">' + item.value + '</span>' + dataName[item.name][item.seriesIndex])
            ).join('<br/>');
        },
      }
    };

    // 初始化图表并绘制
    var densityChart = echarts.init(document.getElementById('densityChart'));
    // 准备 series 数据
    chartConfig.series = Object.keys(rows).map(key => ({
        name: rows[key],
        type: 'line',
        data: Object.values(dataValue).map(item => item[key]),
        showSymbol: false,
        smooth: 0.3,
        emphasis: {
          focus: 'series',
          lineStyle: {
            width: 2,
          },
        },
        blur: {
          lineStyle: {
            opacity: 0.3,
          }
        },
        lineStyle: {
          width: 2,
        },
    }));
    densityChart.setOption(chartConfig);
    densityChart.setOption(chartConfig);
    window.addEventListener('resize', function() {
        densityChart.resize();
    });
  </script>
</body>
</html>
