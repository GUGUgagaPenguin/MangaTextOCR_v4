import sys
import os
from image_processor import process_multiple_images
import filter_results  # 导入filter_results模块
from api_handler import translate_filtered_results  # 导入翻译函数
import merge_results  # 导入merge_results模块
import results2IndesignScript  # 导入results2IndesignScript模块

def main():
    # 设置默认值
    input_dir = "input"
    output_path = "output/results.json"

    
    #输出output\results.json
    process_multiple_images(input_dir, output_path)

    # 调用filter_results.py进行字段过滤 输出output\filtered_results.json
    filter_results.filter_json_fields("output/results.json", "output/filtered_results.json")

    # 调用def translate_filtered_results函数进行翻译 输出output\trans_results.json
    translate_filtered_results("output/filtered_results.json", "output/trans_results.json")

    # 调用merge_results.py进行结果合并 输出output\final_results.json
    merge_results.merge_translation_results("output/results.json", "output/trans_results.json", "output/final_results.json")

    #把final_results.json执行转Indesign脚本操作，输出到output\results2IndesignScript.jsx
    results2IndesignScript.generate_indesign_script()

    
if __name__ == "__main__":
    main()
