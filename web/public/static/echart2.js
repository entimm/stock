function generateChartConfig(data) {
  let seriesData = [];
  for (let key in data) {
    seriesData.push({
      name: key,
      value: data[key]
    });
  }

  return {
    grid: {
      top: '1%',
      left: '1%',
      right: '0%',
      bottom: '1%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: Object.keys(data)
    },
    yAxis: {
      type: 'value',
      position: 'right',
    },
    series: [{
      type: 'line',
      data: seriesData,
      itemStyle: {
        color: 'rgb(246,119,119)'
      },
      areaStyle: {
        color: 'rgb(246,119,119)'
      },
      lineStyle: {
        color: 'rgba(245,91,91,0.5)'
      },
      smooth: 0.4
    }],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
    },
  };
}
