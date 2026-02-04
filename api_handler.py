import os
import base64
import json
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
    # 各地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    # 以下为北京地域的 base_url，若使用弗吉尼亚地域模型，需要将base_url换成https://dashscope-us.aliyuncs.com/compatible-mode/v1
    # 若使用新加坡地域的模型，需将base_url替换为：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

ocr_prompt = """漫画OCR与数据标注专家任务：请对提供的漫画图片进行高精度的日文对话识别，并按照指定的数据结构输出。

具体指令：
1. 识别目标：请识别图片中所有的对话框（气泡）内的日文文本。
2. 文本转录：严格保留原文的日文、断句、标点符号和语气词。不要进行翻译或修改。
3. 坐标检测：检测每个文本区域的界定框（Bounding Box）。
4. 坐标规则：坐标必须基于整张图片的宽高进行归一化处理（百分比），保留4位小数。
5. 坐标定义：x1Ratio/y1Ratio 为界定框左上角，x2Ratio/y2Ratio 为界定框右下角。
6. 元数据填充（严格按照此规则）：
   - id: 生成一个当前时间的毫秒级时间戳作为唯一ID。
   - pageNumber: 统一填写数字 0。
   - textNumber: 按照识别顺序从 1 开始依次递增（如 1, 2, 3...）。
   - transText: 留空字符串 ''。
7. 输出规范：请严格输出以下 JSON 格式的数组，不要包含任何额外的解释、Markdown 代码块标记（如 ```json）或其他文本。

输出格式示例：
[
{
"id": 1770194763943,
"pageNumber": 0,
"textNumber": 1,
"x1Ratio": 0.6603,
"x2Ratio": 0.7984,
"y1Ratio": 0.0746,
"y2Ratio": 0.2359,
"ocrText": "以前話題になったパフォーマンスもだけどどこまで綿密に台本を組んでいるの?",
"transText": ""
}
]

注意事项：请确保识别结果的顺序与漫画阅读顺序（从上到下，从左到右）大致一致。"""


trans_promt = """

{
  "role": "资深日漫本地化翻译专家",
  "task": "请对提供的日文漫画文本进行专业翻译。",
  "instructions": [
    "1. 翻译源：请将输入 JSON 中的 'text' 字段内容从日文翻译为简体中文。",
    "2. 语言风格：",
    "   - 忠实于原意，同时符合中文漫画的阅读习惯和口语化表达。",
    "   - 保持自然流畅，避免生硬的直译。",
    "   - 准确传达角色的语气（如敬语、简体、愤怒、撒娇等）。",
    "3. 特殊处理：",
    "   - 拟声词（如ドキドキ、ゴロゴロ）请根据语境意译为中文拟声词（如'心跳加速'、'雷声轰鸣'）。",
    "   - 语气助词请自然融入中文，不要生硬对应。",
    "   - 人名后缀：xxちゃん -> xx酱；xxさん -> xx桑（或根据身份译为先生/小姐）。",
    "4. 输出结构：",
    "   - 请保持与输入相同的 JSON 结构。",
    "   - 保留原有的 'id' 和 'ocrText' 字段。",
    "   - 将翻译结果存入现有的 'transText' 字段。"
  ],
  "input_example": [
    {
      "id": 1770194763943,
      "ocrText": "以前話題になったパフォーマンスもだけどどこまで綿密に台本を組んでいるの?",
      "transText": ""
    }
  ],
  "output_example": [
    {
      "id": 1770194763943,
      "ocrText": "以前話題になったパフォーマンスもだけどどこまで綿密に台本を組んでいるの?",
      "transText": "之前曾有人谈论过一场演出，但你究竟是如何精心撰写剧本的呢？"
    }
  ],
  "notes": "请只输出包含 'transText' 字段的 JSON 结果，不要包含任何额外的解释、引导语或 Markdown 代码块符号。"
}

"""

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
            model="qwen3-vl-plus", # 此处以qwen3-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/models
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
        return completion.choices[0].message.content
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
            model="qwen3-vl-plus",  # 使用与OCR相同的模型，可根据需要调整
            messages=translation_request,
            timeout=120
        )
        
        # 解析API返回的翻译结果
        response_text = completion.choices[0].message.content
        
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
