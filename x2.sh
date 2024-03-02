set -e

echo 'download-total'
python cmd download-total
echo 'north-funds'
python cmd north-funds

echo 'hot-lose'
python cmd hot-lose

echo 'main-army-up'
python cmd main-army-up
echo 'main-army-down'
python cmd main-army-down

echo 'limit-up-bs'
python cmd limit-up-bs
