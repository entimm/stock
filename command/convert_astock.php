<?php

require dirname(__DIR__).'/vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Spreadsheet;

ini_set('memory_limit', '5120M');

const OPTIONS = [
    'ma5' => 14,
    'ma10' => 15,
    'ma20' => 16,
    'ma60' => 17,
];
define('YEAR', $argv[1] ?? date('Y'));
define('NAMES', require(dirname(__DIR__).'/support/names.php'));

$fileList = require(dirname(__DIR__).'/resources/list.php');
$fileList = array_values(array_filter($fileList, function ($file) {
    return starts_with($file, YEAR);
}));
// $fileList = array_slice($fileList, 0, 100);

function sortBy($arr, $colName, $n = 0, $asc = false)
{
    $arr = array_filter($arr, function ($item) use ($colName) {
        return $item[$colName] !== '' && !is_null($item[$colName]);
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

function readExcel($file)
{
    $spreadsheet = IOFactory::load($file);
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

function readTxt($file)
{
    $fileContent = file_get_contents($file);
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
            'ma5' => $data[13] ?? '',
            'ma10' => $data[14] ?? '',
            'ma20' => $data[15] ?? '',
            'ma60' => $data[16] ?? '',
        ];
    }, $fileLines);

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

function writeCsv($jsonArr, $ma)
{
    $dates = array_keys($jsonArr);

    $rows = [];
    foreach ($jsonArr as $date => $colData) {
        $rows[0][] = $date;
        foreach ($colData[$ma] as $index => $item) {
            $rows[$index + 1][] = $item;
        }
    }

    $csvFile = fopen(dirname(__DIR__).'/resources/processed/' . YEAR . '-' . $ma . '.csv', 'w');
    foreach ($rows as $row) {
        fputcsv($csvFile, $row);
    }
    fclose($csvFile);
}

$jsonArr = [];
$jsonFile = dirname(__DIR__).'/resources/processed/' . YEAR . '.json';
if (file_exists($jsonFile)) {
    $jsonArr = json_decode(file_get_contents($jsonFile), true);
}

$dateListInJson = array_keys($jsonArr);
echo '原先json数据:' . count($jsonArr) . PHP_EOL;
foreach ($fileList as $file) {
    if (in_array($file, $dateListInJson)) continue;
    $fileTxt = dirname(__DIR__)."/resources/raw/tdx_txt/全部Ａ股/全部Ａ股{$file}.txt";
    $fileXls = dirname(__DIR__)."/resources/raw/tdx_excel/全部Ａ股{$file}.xls";
    if (is_file($fileTxt)) {
        $colData = readTxt($fileTxt);
    } elseif (is_file($fileXls)) {
        $colData = readExcel($fileXls);
    } else {
        echo $fileTxt.' 文件不存在'.PHP_EOL;
        echo $fileXls.' 文件不存在'.PHP_EOL;
    }

    $jsonArr[$file] = $colData;
    echo $file . ' SUCCESS' . PHP_EOL;
}
echo '现在json数据:' . count($jsonArr) . PHP_EOL;

file_put_contents($jsonFile, json_encode($jsonArr, JSON_UNESCAPED_UNICODE));

foreach (array_keys(OPTIONS) as $ma) {
    writeCSV($jsonArr, $ma);
}