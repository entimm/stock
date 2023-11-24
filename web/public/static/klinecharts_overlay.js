klinecharts.registerOverlay({
  name: 'chan-text',
  totalStep: 2,
  createPointFigures: ({overlay, coordinates}) => {
    let text = overlay.extendData.text ?? ''
    text = output_text ? text : ''
    let direction = overlay.extendData.direction ?? true
    return [
      {
        type: 'text',
        attrs: {
          x: coordinates[0].x,
          y: coordinates[0].y,
          text: text,
          align: 'center',
          baseline: direction ? 'bottom' : 'top'
        },
        ignoreEvent: true
      }
    ]
  }
});
klinecharts.registerOverlay({
  name: 'chan-segment',
  lock: true,
  totalStep: 3,
  needDefaultPointFigure: false,
  needDefaultXAxisFigure: true,
  needDefaultYAxisFigure: true,
  createPointFigures: ({overlay, coordinates}) => {
    text = output_text ? overlay.extendData : ''
    if (coordinates.length === 2) {
      return [
        {
          type: 'line',
          attrs: {
            coordinates: coordinates
          },
        },
        {
          type: 'text',
          ignoreEvent: true,
          attrs: {
            x: (coordinates[0].x + coordinates[1].x) / 2,
            y: (coordinates[0].y + coordinates[1].y) / 2,
            text: text,
            align: 'center',
            baseline: 'bottom'
          },
        }
      ]
    }
    return []
  }
});
klinecharts.registerOverlay({
  name: 'chan-rect',
  lock: true,
  totalStep: 3,
  needDefaultPointFigure: false,
  needDefaultXAxisFigure: true,
  needDefaultYAxisFigure: true,
  createPointFigures: ({coordinates}) => {
    if (coordinates.length === 2) {
      return [
        {
          type: 'polygon',
          attrs: {
            coordinates: [
              coordinates[0],
              {x: coordinates[1].x, y: coordinates[0].y},
              coordinates[1],
              {x: coordinates[0].x, y: coordinates[1].y}
            ]
          },
          styles: {style: 'stroke_fill'}
        }
      ]
    }
    return []
  }
});
klinecharts.registerOverlay({
  name: 'chan-annotation',
  totalStep: 2,
  styles: {
    text: {
      borderSize: 1,
      borderRadius: 8,
      borderColor: 'rgba(129,1,1,0.5)',
      paddingLeft: 5,
      paddingRight: 5,
      paddingTop: 5,
      paddingBottom: 5,
      backgroundColor: 'rgba(236,171,7,0.8)'
    },
    line: {style: 'dashed', color: 'rgba(129,1,1,0.5)'},
    polygon: {color: 'rgba(129,1,1,0.5)'}
  },
  createPointFigures: ({overlay, coordinates}) => {
    let text = overlay.extendData.text ?? ''
    text = output_text ? text : ''
    let direction = overlay.extendData.direction ?? true
    const startX = coordinates[0].x
    const startY = coordinates[0].y
    const lineEndY = startY - (direction ? 30 : -30)
    return [
      {
        type: 'line',
        attrs: {coordinates: [{x: startX, y: startY}, {x: startX, y: lineEndY}]},
        ignoreEvent: true
      },

      {
        type: 'text',
        attrs: {
          x: startX,
          y: lineEndY,
          text: text,
          align: 'center',
          baseline: direction ? 'bottom' : 'top'
        },
        ignoreEvent: true
      }
    ]
  }
});


////////////////

function barUnionOverlayData(item) {
  return {
    id: `U${item.index}`,
    name: 'chan-rect',
    groupId: 'barUnion',
    lock: true,
    points: [{timestamp: item.begin.time, value: item.begin.value}, {timestamp: item.end.time, value: item.end.value}],
    styles: {
      polygon: {
        color: 'rgba(128, 128, 0, 0.3)',
        borderColor: 'rgba(128, 128, 0, 0.8)',
        borderStyle: item.is_sure ? 'solid' : 'dashed',
        borderDashedValue: [2, 1],
      }
    },
  }
}

function fractalOverlayData(item) {
  return {
    id: `V${item.index}`,
    name: 'chan-text',
    groupId: 'fractal',
    extendData: {
      'direction': item.direction === 'TOP',
      'text': item.direction === 'TOP' ? '∇' : '∆',
    },
    lock: true,
    points: [{timestamp: item.time, value: item.value}],
    styles: {
      text: {
        color: item.direction === 'TOP' ? '#800080' : '#0000FF',
      }
    },
  }
}

function strokeOverlayData(item) {
  var id =`B${item.index}`
  return {
    id: id,
    name: 'chan-segment',
    groupId: 'stroke',
    lock: true,
    extendData: id,
    needDefaultPointFigure: false,
    needDefaultXAxisFigure: false,
    needDefaultYAxisFigure: false,
    points: [{timestamp: item.begin.time, value: item.begin.value}, {timestamp: item.end.time, value: item.end.value}],
    styles: {
      line: {
        color: '#000',
        style: item.is_sure ? 'solid' : 'dashed',
        dashedValue: [10, 5],
        size: 1
      },
      text: {
        color: '#000',
        size: 12
      }
    },
  }
}

function strokeBarOverlayData(item) {
  return {
    id: `BK${item.index}`,
    name: 'chan-rect',
    groupId: 'strokeBar',
    lock: true,
    visible: false,
    points: [{timestamp: item.begin.time, value: item.begin.value}, {timestamp: item.end.time, value: item.end.value}],
    styles: {
      polygon: {
        color: item.direction === 'UP' ? 'rgba(232,7,7,0.3)' : 'rgba(10,145,6,0.3)',
        borderColor: item.direction === 'UP' ? 'rgba(232,7,7,0.8)' : 'rgba(10,145,6,0.8)',
        borderStyle: item.is_sure ? 'solid' : 'dashed',
        borderDashedValue: [10, 5],
      }
    },
  }
}

function segmentOverlayData(item) {
  var id =`S${item.index}`
  return {
    id: id,
    name: 'chan-segment',
    groupId: 'segment',
    lock: true,
    extendData: `${id}-${item.status}`,
    needDefaultPointFigure: false,
    needDefaultXAxisFigure: false,
    needDefaultYAxisFigure: false,
    points: [{timestamp: item.begin.time, value: item.begin.value}, {timestamp: item.end.time, value: item.end.value}],
    styles: {
      line: {
        color: !item.is_trend_1f ? '#de16a5' : '#1620de',
        style: item.is_sure ? 'solid' : 'dashed',
        dashedValue: [10, 5],
        size: 2
      },
      text: {
        color: !item.is_trend_1f ? '#de16a5' : '#1620de',
        size: 15
      }
    },
  }
}