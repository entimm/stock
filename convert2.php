<?php

require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Spreadsheet;

ini_set('memory_limit', '5120M');

$year = $argv[1] ?? '2023';

$fileList = require('file_list.php');

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

$spreadsheet = new Spreadsheet();
$sheet = $spreadsheet->getActiveSheet();

foreach ($fileList as $fileIndex => $file) {
    if (!starts_with($file, $year)) continue;
    $fileNumber = $file;
    $file = "./tdx_txt/行业概念{$file}.txt";
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

    foreach ($data as $key => $value) {
        $sheet->setCellValueByColumnAndRow($fileIndex + 1, $key + 1, $value);
    }

    echo $file . ' SUCCESS' . PHP_EOL;
}

$writer = IOFactory::createWriter($spreadsheet, 'Xlsx');
$writer->save('./' . $year . '.xlsx');