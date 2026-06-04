## Ch01 基于LLM协同辅助自动化测试--Deepseek V3

#### 一、章节概述

本章节将介绍基于DeepSeek API与Gradio的自动化测试用例生成系统。

#### 二、本章目标

1. 理解人工智能技术在软件测试领域的应用场景
2. 掌握使用DeepSeek API生成结构化测试用例的方法
3. 学习使用Gradio构建测试工具交互界面
4. 了解测试用例自动化执行与结果收集的实现方式

#### 三、系统架构概述

1. **系统组成模块**
   - 测试用例生成引擎（DeepSeek API）
   - 数据存储模块（Pandas DataFrame）
   - 用户交互界面（Gradio）
   - 测试执行模块（subprocess）
2. **技术栈**
   - 人工智能：DeepSeek大模型API
   - 数据处理：Pandas库
   - 前端交互：Gradio框架
   - 系统集成：Python subprocess

#### 四、核心代码解析

##### 1. 环境准备

```python
import gradio as gr
import pandas as pd
from openai import OpenAI
import subprocess
```

- **gradio**：用户交互界面
- **pandas**：数据处理库，用于读写Excel文件
- **OpenAI**：OpenAI官方提供的 Python 软件开发工具包（SDK）
- **subprocess**：用于生成和管理子进程，允许 Python 程序调用外部命令或脚本

##### 2. 接入Deepseek V3模型客户端

```python
client = OpenAI(
    api_key="此处填写个人Api-key",
    base_url="https://api.deepseek.com"
)
```

##### 3. 测试用例生成模块

```python
def generate_test_cases(admname_format, admpwd_format):
    # 构造提示词
    prompt = f"""请根据以下要求生成20个登录功能测试用例：

### 字段格式要求：
- admName: {admname_format}
- admPwd: {admpwd_format}

### 测试用例要求：
1. 包含5种正常登录场景（使用符合格式要求的测试数据）
2. 包含10种异常场景：
   - 用户名错误（含特殊字符、超长、空值等）
   - 密码错误（含格式错误、超长、空值等）
   - 用户名密码不匹配
3. 包含5种边界值测试：
   - 用户名长度边界
   - 密码长度边界
   - 特殊字符处理
4. 场景描述为上述正常登录或异常场景的描述
5. 用例ID为自动增长的整数

### 保存Excel文件格式要求：
表格格式：
    |用例ID | 场景描述 | admName | admPwd |
    |------|---------|---------|--------|
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个专业的测试工程师，擅长生成结构化的测试用例"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6
    )
    return response.choices[0].message.content
```

- 结构化提示词设计技巧
- 温度参数(temperature)对生成结果的影响
- 系统角色(System Role)设置的重要性

##### 4. 数据存储模块

```python
def save_to_excel(test_cases, filename="files/testcases.xlsx"):
    lines = test_cases.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    header_line = None
    for line in lines:
        if '|' in line and any(keyword in line for keyword in ['admName', 'admPwd']):  
            #识别表头
            header_line = line
            break
    if header_line is None:
        if len(lines) >= 2:
            header_line = lines
        else:
            return filename
    headers = [h.strip() for h in header_line.split('|') if h.strip()]
    data = []
    start_index = lines.index(header_line) + 2 if header_line in lines else 3
    for line in lines[start_index:]:
        if '|' in line:
            row = [cell.strip() for cell in line.split('|') if cell.strip()]
            if len(row) == len(headers):
                data.append(row)

    if data:
        df = pd.DataFrame(data, columns=headers)
        df.to_excel(filename, index=False)
    return filename
```

- Markdown表格解析技巧
- Pandas DataFrame的应用
- 测试用例的持久化存储

##### 5.生成测试用例，保存Excel

```python
def process_input(admname_format, admpwd_format):
    # 生成测试用例
    test_cases = generate_test_cases(admname_format, admpwd_format)
    # 保存到Excel
    excel_file = save_to_excel(test_cases)
    # 返回格式化后的表格数据
    return test_cases, f"测试用例已保存到 {excel_file}"
```

##### 6.执行测试用例

```python
def run_test_cases():
    try:
        #调用TestCase_Running.py
        result = subprocess.run(['python', 'TestCase_Running.py'],
                              capture_output=True, text=True,encoding='utf-8')
        output = result.stdout
        print(output)
        if result.returncode != 0:
            return f"测试执行失败:\n{output}\n{result.stderr}"
        return f"测试执行成功:\n{output}"
    except Exception as e:
        return f"执行测试时发生错误: {str(e)}"
```

##### 6.1函数功能：

- 执行外部的 `TestCase_Running.py` 测试脚本
- 捕获执行过程中的输出和错误信息
- 根据执行结果返回不同的状态报告

##### 6.2代码结构解析

###### 6.2.1 子进程调用

```python
result = subprocess.run(['python', 'TestCase_Running.py'],
                              capture_output=True, text=True,encoding='utf-8')
```

- 使用 `subprocess.run()` 启动新进程运行测试脚本
- 参数说明：
  - `capture_output=True`：捕获标准输出(stdout)和错误输出(stderr)
  - `text=True`：以文本形式返回输出结果
  - `encoding='utf-8'`：指定输出编码

###### 6.2.2 结果处理

```python
output = result.stdout
if result.returncode != 0:
    return f"测试执行失败:\n{output}\n{result.stderr}"
return f"测试执行成功:\n{output}"
```

- 检查返回码(returncode)：0表示成功，非0表示失败
- 失败时返回输出和错误信息
- 成功时只返回输出信息

##### 7.创建用户交互界面

```python
with gr.Blocks() as demo:
    gr.Markdown("## 测试用例生成器")

    with gr.Row():
        admname_input = gr.Textbox(label="登录用户名的格式要求", placeholder="例如: 由大写字母、小写字母或者数字组成，长度不超过20位")
        admpwd_input = gr.Textbox(label="登录密码的格式要求", placeholder="例如: 长度在6-16位之间")
    with gr.Row():
        submit_btn = gr.Button("生成测试用例")
        run_test_btn = gr.Button("执行测试用例")

    with gr.Row():
        output_table = gr.Markdown(label="生成的测试用例")
        output_message = gr.Textbox(label="操作结果",lines=5, max_lines=20)

    submit_btn.click(
        fn=process_input,
        inputs=[admname_input, admpwd_input],
        outputs=[output_table, output_message]
    )

    run_test_btn.click(
        fn=run_test_cases,
        inputs=[],
        outputs=[output_message]
    )
```

##### 8.启动主程序

```python
if __name__ == '__main__':
    demo.launch()
```

#### 五、总结

1. ##### **技术优势总结**

   - 测试用例生成效率提升
   - 测试场景覆盖度增强
   - 测试文档标准化程度提高

2. ##### **局限性讨论**

   - 对提示词设计的依赖性
   - 生成结果的不可预测性
   - 需要人工验证的必要性

3. ##### **扩展应用方向**

   - 结合传统自动化测试框架
   - 应用于API测试场景
   - 集成到CI/CD流程中