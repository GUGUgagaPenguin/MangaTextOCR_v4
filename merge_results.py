import json
import os
import re

def merge_translation_results(results_file="output/results.json", 
                           trans_file="output/trans_results.json", 
                           output_file="output/final_results.json"):
    """
    将results.json和trans_results.json根据id字段匹配，
    把trans_results.json的翻译结果添加到results.json的完整信息中，
    然后保存到final_results.json
    """
    
    # 检查输入文件是否存在
    if not os.path.exists(results_file):
        print(f"错误：文件 {results_file} 不存在")
        return
    
    if not os.path.exists(trans_file):
        print(f"错误：文件 {trans_file} 不存在")
        return
    
    # 读取results.json文件
    with open(results_file, 'r', encoding='utf-8') as f:
        results_data = json.load(f)
    
    # 读取trans_results.json文件
    with open(trans_file, 'r', encoding='utf-8') as f:
        trans_data = json.load(f)
    
    # 创建一个以id为键的字典，便于快速查找翻译结果
    trans_dict = {}
    for item in trans_data:
        trans_id = item.get('id')
        if trans_id is not None:
            trans_dict[trans_id] = item
    
    # 合并数据：将翻译结果添加到完整信息中
    merged_data = []
    matched_count = 0
    
    for result_item in results_data:
        # 复制原始结果项
        merged_item = result_item.copy()
        
        # 查找对应的翻译结果
        result_id = result_item.get('id')
        if result_id in trans_dict:
            # 找到匹配项，更新transText字段
            trans_item = trans_dict[result_id]
            merged_item['transText'] = trans_item.get('transText', '')
            matched_count += 1
        else:
            # 没有找到匹配项，保持transText为空
            merged_item['transText'] = ''
        
        # 从sourceImage中提取页数信息并更新pageNumber字段
        if 'sourceImage' in result_item:
            source_image = result_item['sourceImage']
            # 使用正则表达式从sourceImage中提取页数
            # 匹配括号中的数字，例如 (004) 或 (4) 或 (04)
            match = re.search(r'\((\d+)\)', source_image)
            if match:
                page_number = int(match.group(1))  # 提取数字部分并转换为整数
                merged_item['pageNumber'] = page_number
            # 如果没有找到匹配的页数，保持原有的pageNumber值不变
        
        merged_data.append(merged_item)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 将合并后的数据保存到新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"合并完成！")
    print(f"总共有 {len(results_data)} 个项目")
    print(f"成功匹配 {matched_count} 个翻译结果")
    print(f"结果已保存到: {output_file}")
    
    return merged_data

if __name__ == "__main__":
    merge_translation_results()
