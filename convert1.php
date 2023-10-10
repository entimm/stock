<?php

require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Spreadsheet;

ini_set('memory_limit', '5120M');

const OPTIONS = [
    'ma5' => 14,
    'ma10' => 15,
    'ma20' => 16,
    'ma60' => 17,
];

$fileList = [
    20230103,
    20230104,
    20230105,
];
$fileList = require('file_list.php');

define('YEAR', $argv[1] ?? '2023');
define('NAMES', require('names.php'));

function sortBy($arr, $colName, $n = 0, $asc = false)
{
    $arr = array_filter($arr, function ($item) use ($colName) {
        return $item[$colName] !== '';
    });
    usort($arr, function ($a, $b) use ($colName, $asc) {
        if ($a[$colName] == $b[$colName]) {
            return 0;
        }

        $r = ($a[$colName] < $b[$colName]) ? -1 : 1;

        return ($asc ? 1 : -1) * $r;
    });

    if ($n) {
        $arr = array_slice($arr, 0, $n);
    }

    $arr = array_map(function ($arr) use ($colName) {
        return $arr['name'] . '|' . $arr[$colName];
    }, $arr);

    return $arr;
}

function readExcel($inputFileName)
{
    $spreadsheet = IOFactory::load($inputFileName);
    $worksheet = $spreadsheet->getActiveSheet();

    $allData = [];
    foreach ($worksheet->getRowIterator() as $row) {
        $item = [];
        preg_match('/\=\"(\d{6})\"/', $worksheet->getCell([1, $row->getRowIndex()])->getValue(), $matches);
        if (empty($matches)) continue;
        $price = $worksheet->getCell([3, $row->getRowIndex()])->getValue();
        if (empty($price)) continue;

        $item['name'] = NAMES[$matches[1]];
        $item['ma5'] = $worksheet->getCell([OPTIONS['ma5'], $row->getRowIndex()])->getValue();
        $item['ma10'] = $worksheet->getCell([OPTIONS['ma10'], $row->getRowIndex()])->getValue();
        $item['ma20'] = $worksheet->getCell([OPTIONS['ma20'], $row->getRowIndex()])->getValue();
        $item['ma60'] = $worksheet->getCell([OPTIONS['ma60'], $row->getRowIndex()])->getValue();
        $allData[] = $item;
    }
    $spreadsheet->disconnectWorksheets();
    unset($spreadsheet);

    $allData = [
        'ma5' => sortBy($allData, 'ma5', 100),
        'ma10' => sortBy($allData, 'ma10', 100),
        'ma20' => sortBy($allData, 'ma20', 100),
        'ma60' => sortBy($allData, 'ma60', 100),
    ];

    return $allData;
}

function starts_with($haystack, $needles)
{
    foreach ((array)$needles as $needle) {
        if ((string)$needle !== '' && strncmp($haystack, $needle, strlen($needle)) === 0) {
            return true;
        }
    }

    return false;
}

function writeExcel($jsonArr, $ma)
{
    $spreadsheet = new Spreadsheet();
    $sheet = $spreadsheet->getActiveSheet();
    $index = 0;
    foreach ($jsonArr as $date => $colData) {
        $sheet->setCellValueByColumnAndRow($index + 1, 1, $date);
        foreach ($colData[$ma] as $rowIndex => $value) {
            $sheet->setCellValueByColumnAndRow($index + 1, $rowIndex + 2, $value);
        }
        $index++;
    }
    $writer = IOFactory::createWriter($spreadsheet, 'Xlsx');
    $writer->save('./ok/' . YEAR . '-' . $ma . '.xlsx');
}

$jsonArr = [];
$jsonFile = './ok/' . YEAR . '.json';
if (file_exists($jsonFile)) {
    $jsonArr = json_decode(file_get_contents($jsonFile), true);
}

$dateListInJson = array_keys($jsonArr);
echo '原先json数据:' . count($jsonArr) . PHP_EOL;
foreach ($fileList as $file) {
    if (!starts_with($file, YEAR)) continue;
    if (in_array($file, $dateListInJson)) continue;
    $fileNumber = $file;
    $file = "./tdx_excel/全部Ａ股{$file}.xls";
    $colData = readExcel($file);

    $jsonArr[$fileNumber] = $colData;
    echo $file . ' SUCCESS' . PHP_EOL;
}
echo '现在json数据:' . count($jsonArr) . PHP_EOL;

file_put_contents($jsonFile, json_encode($jsonArr, JSON_UNESCAPED_UNICODE));

foreach (array_keys(OPTIONS) as $ma) {
    writeExcel($jsonArr, $ma);
}