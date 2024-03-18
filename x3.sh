set -e

python cmd tip

echo 'download-xuangubao-detail'
python cmd  download-xuangubao-detail
echo 'arrange-xuangubao-detail'
python cmd  arrange-xuangubao-detail

echo 'market-height'
python cmd market-height

echo 'download-fs-img'
python cmd download-fs-img

echo 'const-limit'
python cmd const-limit

echo 'cal-limit-up-trend 2'
python cmd cal-limit-up-trend 2
echo 'cal-limit-up-trend 3'
python cmd cal-limit-up-trend 3
echo 'cal-limit-up-trend 5'
python cmd cal-limit-up-trend 5
echo 'cal-limit-up-trend 10'
python cmd cal-limit-up-trend 10
