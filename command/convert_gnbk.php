<?php

require dirname(__DIR__).'/vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Spreadsheet;

ini_set('memory_limit', '5120M');

define('YEAR', $argv[1] ?? date('Y'));

$fileList = require(dirname(__DIR__).'/resources/list.php');
$fileList = array_values(array_filter($fileList, function ($file) {
    return starts_with($file, YEAR);
}));
// $fileList = array_slice($fileList, 0, 20);

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

function readTxt($filePath)
{
    $fileContent = file_get_contents($filePath);
    $fileContent = mb_convert_encoding($fileContent, 'UTF-8', 'GBK');
    $fileContent = preg_replace('/\t/', ',', $fileContent);
    $fileLines = explode(PHP_EOL, $fileContent);
    array_shift($fileLines);
    array_shift($fileLines);
    array_pop($fileLines);
    array_pop($fileLines);
    $allData = array_map(function ($item) {
        $data = explode(',', $item);
        return [
            'name' => $data[1],
            'ma5' => $data[5] ?? '',
            'ma10' => $data[6] ?? '',
            'ma20' => $data[7] ?? '',
            'ma60' => $data[8] ?? '',
            'total' => $data[9] ?? '',
        ];
    }, $fileLines);

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


$dataList = [];
foreach ($fileList as $fileIndex => $file) {
    $fileNumber = $file;
    $file = dirname(__DIR__)."/resources/raw/tdx_txt/行业概念/行业概念{$file}.txt";
    $colData = readTxt($file);

    $data = array_merge(
        [$fileNumber],
        sortBy($colData, 'ma5', 20),
        ['', ''],
        sortBy($colData, 'total', 20),
        ['', ''],
        sortBy($colData, 'ma5', 20, true),
        ['', ''],
        sortBy($colData, 'total', 20, true)
    );

    $dataList[] = $data;
}

$newDataList = [];
foreach ($dataList as $colIndex => $valueList) {
    foreach ($valueList as $rowIndex => $value) {
        $newDataList[$rowIndex][] = $value;
    }
}

$csvFile = fopen(dirname(__DIR__).'/resources/processed/GNBK' . YEAR . '.csv', 'w');
foreach ($newDataList as $row) {
    fputcsv($csvFile, $row);
}
fclose($csvFile);
