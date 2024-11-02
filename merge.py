import os
import csv

# 设置输入和输出路径
source_dir = os.path.join(os.path.dirname(__file__), 'Data', 'zhCN')
output_file = os.path.join(os.path.dirname(__file__), 'Localizations', 'zhCN.csv')

# 确保输出目录存在
os.makedirs(os.path.dirname(output_file), exist_ok=True)

print(f'清空并合并CSV文件，从 "{source_dir}" 到 "{output_file}"')

# 打开输出文件并清空（通过 'w' 模式）
with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["ID", "Text", "Comment"])  # 写入标题行

    # 遍历 source_dir 中的每个 CSV 文件
    for filename in os.listdir(source_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(source_dir, filename)
            print(f'正在合并 "{file_path}"...')

            # 打开文件并跳过标题行
            with open(file_path, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                next(reader, None)  # 跳过标题行
                # 将文件内容写入输出文件
                for row in reader:
                    writer.writerow(row)

print("CSV文件已成功合并。")
