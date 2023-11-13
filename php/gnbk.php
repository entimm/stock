<?php

require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Cell\Coordinate;

function readEvenColumnsFromRow($filePath, $rowNumbers, $type) {
    $result = [];
    $file = new SplFileObject($filePath, 'r');
    $dataList = $file->fgetcsv();
    foreach($rowNumbers as $rowNumber) {
        $file->seek($rowNumber + 22 * $type);
        $row = $file->fgetcsv();
        foreach($row as $colIndex => $value) {
            $date = $dataList[$colIndex];
            $arr = explode('|', $value);
            $result['name'][$date][] = $arr[0];
            $result['value'][$date][] = $arr[1];
        }
    }

    return $result;
}

$typeList = [
    '超短↖',
    '综合↖',
    '超短↘',
    '综合↘',
];
$yearList = range(date('Y'), 2018);
$lineList = [
  '1,2,3,4,5',
  '5,10,15,20',
];

$type = $_GET['type'] ?? '0';
$year = $_GET['year'] ?? $yearList[0];
$lineId = $_GET['line_id'] ?? 0;

$rows = explode(',', $lineList[$lineId]);

$filePath = dirname(__DIR__)."/resources/processed/GNBK{$year}.csv";

$data = readEvenColumnsFromRow($filePath, $rows, $type);
?>

<!DOCTYPE html>
<html>
<head>
  <title>A股概念趋势图 - <?=$typeList[$type]?></title>
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

    .fixed-links1 {
      position: fixed;
      top: 0;
      right: 0;
      margin: 20px 40px;
      z-index: 9999; 
    }
    .fixed-links2 {
      position: fixed;
      top: 50px;
      right: 0;
      margin: 20px 40px;
      z-index: 9999; 
    }
    .fixed-links3 {
      position: fixed;
      top: 100px;
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
    <div class="fixed-links1">
        <?php foreach ($typeList as $key => $value): ?>
            <a href="?type=<?=$key?>&year=<?=$year?>&line_id=<?=$lineId?>" <?php if ($key == $type): ?>class="highlight"<?php endif ?>><?=$value?></a>
        <?php endforeach ?>
    </div>
    <div class="fixed-links2">
        <?php foreach ($yearList as $value): ?>
            <a href="?type=<?=$type?>&year=<?=$value?>&line_id=<?=$lineId?>" <?php if ($value == $year): ?>class="highlight"<?php endif ?>><?=$value?></a>
        <?php endforeach ?>
    </div>
    <div class="fixed-links3">
        <?php foreach ($lineList as $key => $value): ?>
            <a href="?type=<?=$type?>&year=<?=$year?>&line_id=<?=$key?>" <?php if ($lineId == $key): ?>class="highlight"<?php endif ?>>线<?=$key?></a>
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
        interval: 3,
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
              item => (item.marker + '<span style="display:inline-block;width:60px">' + item.seriesName  + '</span>' + '<span style="display:inline-block;width:50px">' + item.value + '</span>' + dataName[item.name][item.seriesIndex])
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
    window.addEventListener('resize', function() {
        densityChart.resize();
    });
  </script>
</body>
</html>
