set -e

echo 'mv-raw'
python cmd mv-raw
echo 'convert-astock'
python cmd convert-astock
echo 'convert-gnbk'
python cmd convert-gnbk
echo 'convert-gnbk-trend-up'
python cmd convert-gnbk-trend-up
echo 'convert-gnbk-trend-down'
python cmd convert-gnbk-trend-down

echo 'cal-trend-ptg 2'
python cmd cal-trend-ptg 2
echo 'cal-trend-ptg 3'
python cmd cal-trend-ptg 3
echo 'cal-trend-ptg 5'
python cmd cal-trend-ptg 5
echo 'cal-trend-ptg 10'
python cmd cal-trend-ptg 10
echo 'cal-trend-ptg 20'
python cmd cal-trend-ptg 20
echo 'cal-trend-ptg 60'
python cmd cal-trend-ptg 60

echo 'cal-new-high'
python cmd cal-new-high
echo 'cal-new-high-freq 20'
python cmd cal-new-high-freq 20
echo 'cal-new-high-freq 60'
python cmd cal-new-high-freq 60
echo 'cal-new-high-freq 12 5'
python cmd cal-new-high-freq 12 5

echo 'backtest-trend-monster'
python cmd backtest-trend-monster