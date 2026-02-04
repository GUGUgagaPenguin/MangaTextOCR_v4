import os
import base64
import json
import yaml
from openai import OpenAI

# 读取配置文件
with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)

client = OpenAI(
    api_key=config['api']['key'],
    base_url=config['api']['base_url'],
)

ocr_prompt = config['prompts']['ocr_prompt']
trans_promt = config['prompts']['trans_prompt']
ocr_model = config['api']['ocr_model']
trans_model = config['api']['trans_model']

# 将本地图片转换为base64编码
def local_image_to_data_url(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        print(f"错误：找不到图片文件 {image_path}")
        print("请确保图片文件存在，或使用在线图片URL")
        return None


# 处理单个图片
def process_single_image(image_path):
    import time
    print(f"正在处理图片: {image_path}")
    img_url = local_image_to_data_url(image_path)

    # 检查图片是否成功加载
    if img_url is None:
        print(f"跳过图片: {image_path} (无法加载)")
        return None

    try:
        print(f"开始向API发送请求...")
        start_time = time.time()
        completion = client.chat.completions.create(
            model=ocr_model, # 此处以qwen3-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/models
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_url  # 使用本地图片的data URL
                            },
                        },
                        {"type": "text", "text": ocr_prompt},  # 使用变量
                    ],
                },
            ],
            timeout=120  # 增加到120秒超时，给复杂图片更多处理时间
        )
        end_time = time.time()
        print(f"API响应成功，耗时: {end_time - start_time:.2f}秒")
        
        # 检查completion对象是否有效
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            return completion.choices[0].message.content
        else:
            print(f"API响应格式异常: {completion}")
            return None
    except Exception as e:
        end_time = time.time()
        print(f"处理图片时发生错误 {image_path}: {str(e)} (耗时: {end_time - start_time:.2f}秒)")
        return None


# 翻译filtered_results.json中的文本
def translate_filtered_results(input_file="output/filtered_results.json", output_file="output/trans_results.json"):
    """
    读取filtered_results.json文件，使用trans_promt提示词发送翻译请求，
    将返回的翻译结果保存到trans_results.json文件
    """
    import time
    import json
    import os
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        return None
    
    # 读取filtered_results.json文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"开始翻译 {len(data)} 条记录...")
    
    try:
        # 创建翻译请求的消息，一次性发送整个数据集
        translation_request = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": trans_promt},
                    {"type": "text", "text": json.dumps(data, ensure_ascii=False)}
                ],
            },
        ]
        
        # 发送翻译请求
        completion = client.chat.completions.create(
            model=trans_model,  # 使用与OCR相同的模型，可根据需要调整
            messages=translation_request,
            timeout=120
        )
        
        # 解析API返回的翻译结果
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            response_text = completion.choices[0].message.content
        else:
            print(f"翻译API响应格式异常: {completion}")
            # 如果解析失败，使用原始数据，但transText保持为空
            translated_data = []
            for item in data:
                updated_item = item.copy()
                updated_item['transText'] = ''
                translated_data.append(updated_item)
            return translated_data
        
        # 尝试解析返回的JSON
        try:
            parsed_response = json.loads(response_text)
            
            # 确保返回的是数组格式
            if isinstance(parsed_response, list):
                translated_data = []
                
                # 遍历返回的翻译结果，与原始数据进行匹配
                for i, translated_item in enumerate(parsed_response):
                    if i < len(data):  # 确保索引不越界
                        original_item = data[i]
                        
                        # 创建新的条目，保留原始数据并更新transText
                        updated_item = original_item.copy()
                        updated_item['transText'] = translated_item.get('transText', translated_item.get('translated_text', ''))
                        
                        translated_data.append(updated_item)
                    else:
                        # 如果返回的条目数量超过原始数据，跳过多余的条目
                        break
                
                # 如果返回的条目少于原始数据，为剩余条目添加空的transText
                if len(parsed_response) < len(data):
                    for i in range(len(parsed_response), len(data)):
                        original_item = data[i]
                        updated_item = original_item.copy()
                        updated_item['transText'] = ''
                        translated_data.append(updated_item)
                
                print(f"成功翻译 {len(translated_data)} 条记录")
            else:
                print("翻译失败：API返回格式不正确")
                # 如果解析失败，使用原始数据，但transText保持为空
                translated_data = []
                for item in data:
                    updated_item = item.copy()
                    updated_item['transText'] = ''
                    translated_data.append(updated_item)
        except json.JSONDecodeError:
            print(f"翻译失败：无法解析API返回的JSON")
            print(f"API返回内容: {response_text}")
            # 如果解析失败，使用原始数据，但transText保持为空
            translated_data = []
            for item in data:
                updated_item = item.copy()
                updated_item['transText'] = ''
                translated_data.append(updated_item)
    
    except Exception as e:
        print(f"翻译时发生错误: {str(e)}")
        # 如果API调用失败，使用原始数据，但transText保持为空
        translated_data = []
        for item in data:
            updated_item = item.copy()
            updated_item['transText'] = ''
            translated_data.append(updated_item)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 将翻译结果保存到新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
    
    print(f"翻译完成！结果已保存到: {output_file}")
    return translated_data
