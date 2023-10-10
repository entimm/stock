<?php

$newValueList = array_slice($argv, 1);
if (!$newValueList) $newValueList = [date('Ymd')];

$data = require dirname(__DIR__).'/resources/list.php';

// 将新值添加到数组中
$data = array_unique(array_merge($data, $newValueList));

sort($data);

// 将更新后的数组写回到文件中
file_put_contents(dirname(__DIR__).'/resources/list.php', '<?php return ' . var_export($data, true) . ';');

echo implode(', ', $newValueList)."已成功添加到数组中。".PHP_EOL;
