# MangaTextOCR_v4
<<<<<<< HEAD

一个自动化漫画文本识别、翻译和InDesign集成工具。

## 简介

MangaTextOCR_v4 是一个专门用于处理漫画图像的工具，能够自动识别图像中的日文文本，将其翻译成中文，并生成可用于Adobe InDesign的脚本。该项目特别适用于漫画本地化工作流程。

## 功能特性

- 自动识别漫画图像中的文本气泡
- 高精度OCR文本提取
- 日文到中文的专业翻译
- 自动生成InDesign脚本
- 支持批量处理多张图片
- 保持原文本位置信息

## 依赖要求

- Python 3.7+
- OpenAI兼容API
- PyYAML
- OpenAI Python库

## 安装

### 方法一：使用虚拟环境（推荐）

1. 克隆项目到本地
2. 创建虚拟环境：
   ```
   python -m venv venv
   ```
3. 激活虚拟环境：
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. 使用requirements.txt安装依赖：
   ```
   pip install -r requirements.txt
   ```

### 方法二：直接安装

1. 克隆项目到本地
2. 安装Python依赖：
   ```
   pip install openai pyyaml
   ```

## 配置

在使用前，需要配置API信息：

1. 复制 `config.yaml.example` 文件并重命名为 `config.yaml`
2. 编辑 `config.yaml` 文件，更新以下字段：
   - `api.key`: 您的API密钥
   - `api.base_url`: API基础URL
   - `prompts.ocr_prompt`: OCR提示词（最好不要动哦）
   - `prompts.trans_prompt`: 翻译提示词（最好不要动哦）

注意：`config.yaml` 文件已添加到 `.gitignore` 中，您的API密钥不会意外提交到版本控制系统。

## 使用方法

1. 将待处理的漫画图片放入 `input/` 目录
2. 运行主程序：
   ```
   python main.py
   ```
3. 程序将自动执行以下步骤：
   - 图像OCR处理
   - 文本过滤
   - 翻译处理
   - 结果合并
   - 生成InDesign脚本

## 项目结构

- `main.py`: 主程序入口，协调各模块工作
- `image_processor.py`: 图像处理模块
- `api_handler.py`: API接口处理模块
- `filter_results.py`: 结果过滤模块
- `merge_results.py`: 结果合并模块
- `results2IndesignScript.py`: 生成InDesign脚本模块
- `config.yaml`: 配置文件
- `input/`: 输入图片目录
- `output/`: 输出结果目录

## 工作流程

1. **图像处理**: 从 `input/` 目录读取图片，使用OCR识别文本
2. **结果过滤**: 提取关键字段，生成标准化的JSON格式
3. **翻译处理**: 将日文文本翻译为中文
4. **结果合并**: 将原文、译文和位置信息合并
5. **InDesign脚本生成**: 生成可在Adobe InDesign中使用的JavaScript脚本

## 输出文件

- `output/results.json`: 初始OCR结果
- `output/filtered_results.json`: 过滤后的结果
- `output/trans_results.json`: 翻译结果
- `output/final_results.json`: 最终合并结果
- `output/results2IndesignScript.jsx`: InDesign脚本

## InDesign脚本使用

生成的 `results2IndesignScript.jsx` 文件可以直接在Adobe InDesign中运行，它会：
- 根据原始文本位置放置翻译后的文本
- 自动处理单双页位置偏移
- 设置垂直文本方向

## 注意事项

- 确保API密钥有效且有足够配额
- 输入图片应为高质量扫描件以获得最佳OCR效果
- 翻译质量取决于所使用的AI模型
- 请遵守相关版权法规，仅用于合法授权的内容
=======
Automated manga text recognition, translation, and InDesign integration tool
>>>>>>> 1cea773ca559f6c784a835d8b19b5e8f19b9b1df
