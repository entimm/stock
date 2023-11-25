// 创建数据密度图的配置
let chartConfig = {
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
    interval: yAxisInterval,
    position: 'right',
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
        item => (item.marker + '<span style="display:inline-block;width:60px">' + item.seriesName + '</span>' + '<span style="display:inline-block;width:50px">' + item.value + '</span>' + dataName[item.name][item.seriesIndex])
      ).join('<br/>');
    },
  }
};

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

// 初始化图表并绘制
let chart = echarts.init(document.getElementById('chart'));
chart.setOption(chartConfig);
window.addEventListener('resize', function () {
  chart.resize();
});