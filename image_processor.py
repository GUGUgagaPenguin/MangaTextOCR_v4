import os
import json
import fnmatch


# 获取输入目录中的所有图片文件
def get_image_files(input_dir="input"):
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff']
    all_files = os.listdir(input_dir)
    image_files = []
    for file in all_files:
        for ext in image_extensions:
            if fnmatch.fnmatch(file.lower(), ext):  # 只匹配小写形式避免重复
                image_files.append(os.path.join(input_dir, file))
    return sorted(list(set(image_files)))  # 使用set去重并排序


# 主函数：处理多个图片
def process_multiple_images(input_dir="input", output_path="output/results.json"):
    from api_handler import process_single_image
    import signal
    import time
    
    image_files = get_image_files(input_dir)
    
    if not image_files:
        print("在输入目录中未找到任何图片文件")
        return

    print(f"找到 {len(image_files)} 个图片文件: {image_files}")

    all_results = []  # 存储所有图片的处理结果

    for i, image_path in enumerate(image_files, 1):
        print(f"\n--- 处理第 {i}/{len(image_files)} 张图片 ---")
        print(f"当前处理图片: {os.path.basename(image_path)}")
        result = process_single_image(image_path)
        
        if result:
            print(f"图片 '{image_path}' 的处理结果:")
            print(result)
            
            # 尝试解析JSON结果并添加到总结果中
            try:
                parsed_result = json.loads(result)
                # 为每个结果添加图片路径信息
                for item in parsed_result:
                    item['sourceImage'] = os.path.basename(image_path)
                all_results.extend(parsed_result)
            except json.JSONDecodeError as e:
                print(f"解析JSON时出错 {image_path}: {str(e)}")
        else:
            print(f"未能处理图片 '{image_path}'")
            # 记录失败的图片以便后续分析
            print(f"警告: 图片处理失败，继续处理下一张图片...")
    
    # 创建输出目录（如果不存在）
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 将合并的结果保存到output文件夹
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n所有图片处理完成！合并结果已保存到: {output_path}")
    print(f"总共识别到 {len(all_results)} 个文本元素")
    
    return all_results
