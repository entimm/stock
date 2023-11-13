import os
import re


def rename_xls_to_txt(directory, filename):
    old_path = os.path.join(directory, filename)
    new_filename = os.path.splitext(filename)[0] + '.txt'
    new_path = os.path.join(directory, new_filename)

    os.rename(old_path, new_path)
    print(f'Renamed: {filename} to {new_filename}')

    return new_path


def process_text_files(directory='.'):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith('.xls'):
            file_path = rename_xls_to_txt(directory, filename)

        if not file_path.endswith('.txt'):
            continue

        try:
            with open(file_path, 'r', encoding='gbk') as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='utf8') as file:
                content = file.read()

        # 使用正则表达式进行匹配和替换
        updated_content = re.sub(r'="(\d{6})"', r'\1', content)

        # 将更新后的内容写回文件
        with open(file_path, 'w', encoding='gbk') as file:
            file.write(updated_content)

        print(f'Processed: {filename}')


if __name__ == '__main__':
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    tdx_xls_path = os.path.join(root_path, 'resources', 'raw', 'tdx_excel')

    process_text_files(tdx_xls_path)
