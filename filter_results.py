import json
import os

def filter_json_fields(input_file, output_file):
    """
    从输入的JSON文件中只保留id、ocrText和transText字段，并保存到输出文件
    
    Args:
        input_file (str): 输入JSON文件路径
        output_file (str): 输出JSON文件路径
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        return
    
    # 读取原始JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 过滤数据，只保留指定的字段
    filtered_data = []
    for item in data:
        filtered_item = {}
        # 只保留id、ocrText和transText字段
        for field in ['id', 'ocrText', 'transText']:
            if field in item:
                filtered_item[field] = item[field]
        filtered_data.append(filtered_item)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 将过滤后的数据保存到新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    print(f"过滤完成！精简后的数据已保存到: {output_file}")
    print(f"共处理了 {len(filtered_data)} 个条目")

if __name__ == "__main__":
    # 默认输入和输出文件路径
    input_file = "output/results.json"
    output_file = "output/filtered_results.json"
    
    # 执行过滤操作
    filter_json_fields(input_file, output_file)
