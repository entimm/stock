<?php

require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Spreadsheet;

ini_set('memory_limit', '5120M');

class Store
{
    const OPTIONS = [
        'ma5' => 14,
        'ma10' => 15,
        'ma20' => 16,
        'ma60' => 17,
    ];
    static $names;
    static $ma;
}

$year = $argv[1] ?? '2023';

$fileList = require('file_list.php');
Store::$names = require('names.php');

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

        $item['name'] = $matches[1];
        $item['name'] = Store::$names[$matches[1]];
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
    if (!starts_with($file, $year)) continue;
    $fileNumber = $file;
    $file = "./tdx_excel/全部Ａ股{$file}.xls";
    $colData = readExcel($file);
    array_unshift($colData, $fileNumber);
    $jsonArr[] = $colData;
    echo $file.' SUCCESS'.PHP_EOL;
}

$jsonFile = './'.$year.'-hello.json';
file_put_contents($jsonFile, json_encode($jsonArr, JSON_UNESCAPED_UNICODE));