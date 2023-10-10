<?php

require dirname(__DIR__).'/vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;

ini_set('memory_limit', '5120M');

$year = $argv[1] ?? date('Y');

$data = require dirname(__DIR__).'/resources/list.php';
$fileList = array_values(array_filter($fileList, function ($file) {
    return starts_with($file, YEAR);
}));
define('NAMES', require(dirname(__DIR__).'/support/names.php'));

function readExcel($inputFileName)
{
    // 读取文件
    $spreadsheet = IOFactory::load($inputFileName);
    $worksheet = $spreadsheet->getActiveSheet();

    // 循环遍历行，以及行中的数据
    $allData = [];
    foreach ($worksheet->getRowIterator() as $row) {
        $item = [];
        preg_match('/\=\"(\d{6})\"/', $worksheet->getCell([1, $row->getRowIndex()])->getValue(), $matches);
        if (empty($matches)) continue;
        $price = $worksheet->getCell([3, $row->getRowIndex()])->getValue();
        if (empty($price)) continue;

        $item['name'] = NAMES[$matches[1]];
        $item['change'] = $price;
        if ($item['change'] >= 30) {
            $allData[] = $item;
        }
    }
    $spreadsheet->disconnectWorksheets();
    unset($spreadsheet);

    return $allData;
}

function starts_with($haystack, $needles)
{
    foreach ((array) $needles as $needle) {
        if ((string) $needle !== '' && strncmp($haystack, $needle, strlen($needle)) === 0) {
            return true;
        }
    }

    return false;
}

$jsonArr = [];
foreach($fileList as $fileIndex => $file) {
    $fileNumber = $file;
    $file = dirname(__DIR__)."/resources/raw/tdx_excel/全部Ａ股{$file}.xls";
    $colData = readExcel($file);
    array_unshift($colData, $fileNumber);
    $jsonArr[] = $colData;
    echo $file.' SUCCESS'.PHP_EOL;
}

$jsonFile = dirname(__DIR__).'/resources/'.$year.'-spec.json';
file_put_contents($jsonFile, json_encode($jsonArr, JSON_UNESCAPED_UNICODE));