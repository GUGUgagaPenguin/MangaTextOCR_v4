import sys
import os
from image_processor import process_multiple_images

def main():
    # 设置默认值
    input_dir = "input"
    output_path = "output/results.json"
    
    # 如果提供了命令行参数，则使用它们
    if len(sys.argv) == 3:
        input_dir = sys.argv[1]
        output_path = sys.argv[2]
    elif len(sys.argv) != 1:
        print("用法: python main.py [<输入图片目录> <输出JSON文件路径>]")
        print("如果未提供参数，则默认输入目录为 'input'，输出文件为 'output/results.json'")
        sys.exit(1)
    
    # 确保输入目录存在
    if not os.path.exists(input_dir):
        print(f"错误: 输入目录 '{input_dir}' 不存在")
        sys.exit(1)
    
    process_multiple_images(input_dir, output_path)

if __name__ == "__main__":
    main()
