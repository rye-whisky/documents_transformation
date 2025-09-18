# 🚀 文档转换工具 📄✨

一个超酷的独立文档转换工具，支持将PDF和Word文档转换为Markdown格式，通过智谱AI API进行智能文档内容提取！🎉

## ✨ 功能特性

- 📄 **多格式支持**: 支持PDF和Word(.doc/.docx)文档，格式全覆盖！
- 🤖 **AI驱动**: 使用智谱AI GLM-4.5V模型进行智能文档内容提取，超智能！💡
- 📊 **表格处理**: 增强的表格识别和转换功能，确保表格完美转换为Markdown格式！📋
- 🔄 **重试机制**: 完善的超时处理和重试机制，提高处理稳定性，再也不怕失败！🛡️
- 📦 **批量处理**: 支持批量处理多个文档文件，效率翻倍！⚡
- 🎯 **精确提取**: 保持原文档结构和语义完整性，细节完美保留！🎨
- 📖 **大文件支持**: 智能分页处理大文档，轻松处理8MB+文件！📚
- 🚀 **高性能优化**: 动态token管理，智能处理策略，速度与质量并存！🔥

## 📁 项目结构

```
documents_transformation/
📦 核心结构一览：
├── src/                          # 📂 源代码目录
│   ├── __init__.py              # 🐍 包初始化
│   ├── base_workflow.py          # 🏗️ 基础工作流类
│   └── unified_content_extraction_workflow.py  # 🎯 统一内容抽取工作流
├── config/                       # ⚙️ 配置文件目录
│   ├── __init__.py
│   └── model_config.yaml         # 🤖 模型配置文件
├── prompts/                      # 💭 提示词目录
│   ├── __init__.py
│   └── document_extraction_prompts.yaml  # 📝 文档提取提示词
├── utils/                        # 🛠️ 工具函数目录
│   ├── __init__.py
│   ├── model_loader.py           # 🔌 模型加载器
│   └── document_extractor.py     # 🎣 文档抽取器
├── tests/                        # 🧪 测试目录
│   └── __init__.py
├── output/                       # 📤 输出目录
├── process_documents.py          # 🚀 主程序入口
├── requirements.txt              # 📦 依赖包列表
└── README.md                     # 📖 项目说明文档
```

## 🛠️ 安装依赖

```bash
pip install -r requirements.txt
```
🎉 一键安装所有依赖，超简单！🎉

## ⚙️ 配置说明

### 🔑 1. 环境变量

创建 `.env` 文件并设置API密钥：

```env
ZHIPUAI_API_KEY=your_zhipu_api_key_here
```
🔑 这是你的AI魔法钥匙，一定要保管好哦！🔑

### 🤖 2. 模型配置

编辑 `config/model_config.yaml` 文件，配置模型参数：

```yaml
models:
  glm-4.5-air:
    provider: zhipu
    model_name: glm-4v-air
    api_key: ${ZHIPUAI_API_KEY}
    temperature: 0.3
    api_base: https://open.bigmodel.cn/api/paas/v4
  
  glm-4.5v:
    provider: zhipu
    model_name: glm-4v
    api_key: ${ZHIPUAI_API_KEY}
    temperature: 0.3
    api_base: https://open.bigmodel.cn/api/paas/v4
```
🎛️ 调整这些参数，让你的AI助手更懂你！🎛️

## 🚀 使用方法

### 📁 输入文件说明

#### 📂 支持的输入格式
- **PDF文件**: `.pdf` 格式，支持各种版本的PDF文档
- **Word文件**: `.doc` 和 `.docx` 格式，兼容新旧版本
- **文件大小**:
  - 小文件: < 10MB (常规处理)
  - 大文件: ≥ 10MB (自动启用分页处理)
  - 最大支持: 50MB

#### 📁 输入目录结构

📁 将需要处理的文档放入输入目录，程序会自动扫描并处理！📁

📝 文件命名建议
- 使用有意义的文件名，便于识别
- 避免使用特殊字符和空格
- 中文文件名完全支持，无需转换

### 📤 输出文件说明

#### 📂 输出目录结构

📤 输出文件自动保存为Markdown格式，文件名保持原文件名并添加`_extracted_content`后缀！📤

📄 输出格式特性
- **文件格式**: Markdown (.md)
- **编码格式**: UTF-8
- **内容结构**:
  ```markdown
  # 文档标题
  
  ## 章节1
  章节内容...
  
  ## 章节2
  章节内容...
  
  ---
  
  表格内容:
  | 列1 | 列2 | 列3 |
  |-----|-----|-----|
  | 数据1 | 数据2 | 数据3 |
  
  ---
  
  ![图片描述](图片信息)
  ```
  
#### 📊 输出内容质量
- 📝 **完整提取**: 提取所有文本内容，包括页眉页脚
- 🏗️ **结构保留**: 保持原文档的章节结构和层级关系
- 📋 **表格转换**: 表格完美转换为Markdown格式
- 🖼️ **图片信息**: 图片描述和位置信息完整保留
- 🔤 **格式保留**: 加粗、斜体等格式正确转换
- 🎯 **智能分页**: 大文档自动分页处理，内容完整无缺

### 💻 命令行使用

```bash
# 处理指定目录中的所有文档
python process_documents.py

# 或者直接修改代码中的目录路径
if __name__ == "__main__":
    input_directory = "your_input_directory"
    output_directory = "your_output_directory"
    process_documents(input_directory, output_directory)
```
🎯 一键处理，超级简单！🎯

### 🐍 编程接口使用

```python
from documents_transformation.src.unified_content_extraction_workflow import UnifiedContentExtractionWorkflow
import asyncio

# 初始化工作流
workflow = UnifiedContentExtractionWorkflow(
    base_dir="input_directory",
    output_dir="output_directory"
)

# 处理PDF文件
async def process_pdf():
    result = await workflow.run_from_file("example.pdf", "pdf")
    if result:
        print("🎉 PDF处理成功！")
        print(result)

# 处理Word文件
async def process_docx():
    result = await workflow.run_from_file("example.docx", "docx")
    if result:
        print("🎉 Word处理成功！")
        print(result)

# 运行
asyncio.run(process_pdf())
# 或者
asyncio.run(process_docx())
```
🎨 灵活编程，随心所欲！🎨

## 📄 输出格式

处理后的文档将保存为Markdown格式，包含以下特性：

- 📝 **完整内容**: 提取文档中的所有文本内容，一个都不漏！
- 🏗️ **结构保留**: 保持原文档的章节结构和层级关系，完美还原！
- 📊 **表格处理**: 表格正确转换为Markdown表格格式，清晰美观！
- 🖼️ **图片处理**: 图片信息以Markdown语法保存，图文并茂！
- 📋 **列表支持**: 有序和无序列表的正确转换，层次分明！
- 🔤 **格式保留**: 保留原文档的强调格式（加粗、斜体等），样式不变！
- 🎯 **智能分页**: 大文档自动分页处理，内容完整无缺！
- 🌟 **高质量输出**: 专业的Markdown格式，可直接使用！

## ⚡ 性能优化

- 📦 **批量处理**: 支持批量处理多个文档，效率翻倍！
- 🔄 **重试机制**: 自动重试失败的请求，提高稳定性，永不放弃！
- ⏱️ **超时控制**: 合理的超时设置，避免长时间等待，体验流畅！
- 💾 **内存优化**: 流式处理大文件，减少内存占用，资源友好！
- 🎯 **智能分块**: 大文件智能分块处理，突破token限制！
- 🚀 **动态调整**: 根据文件大小动态调整处理策略，性能最优！

## ⚠️ 注意事项

1. 🔑 **API密钥**: 确保已正确设置智谱AI的API密钥，这是魔法钥匙！
2. 🌐 **网络连接**: 需要稳定的网络连接访问智谱AI API，网络要给力哦！
3. 📁 **文件大小**: 建议单文件大小不超过50MB，大文件也能处理！
4. 🔄 **并发限制**: 注意API的并发调用限制，不要贪心哦！
5. 🛡️ **错误处理**: 程序包含完善的错误处理机制，安心使用！
6. 💾 **内存管理**: 大文件处理时注意内存使用，建议关闭其他大程序！
7. 📝 **输出目录**: 确保输出目录有写入权限，不然文件保存不了哦！

## 🔧 故障排除

### ❓ 常见问题

1. 🔑 **API密钥错误**
   - 检查 `.env` 文件中的API密钥是否正确
   - 确认API密钥有效且未过期
   - 🔍 确保没有多余的空格或特殊字符！

2. 🌐 **网络连接问题**
   - 检查网络连接是否正常
   - 确认防火墙设置是否允许访问API服务器
   - 📶 尝试切换网络或重启路由器！

3. 📁 **文件处理失败**
   - 确认文件格式支持（PDF、Word）
   - 检查文件是否损坏或过大
   - 🔄 尝试重新下载或修复文件！

4. ⏱️ **超时问题**
   - 增加超时时间设置
   - 检查网络延迟情况
   - 🚀 网络好的时候再处理大文件！

5. 📂 **输出目录问题**
   - 确保输出目录存在且有写入权限
   - 📁 检查磁盘空间是否充足！

### 📊 日志查看

程序运行时会输出详细的日志信息，包括：
- 📤 文件上传状态
- 🤖 API调用情况
- ❌ 错误信息
- 📈 处理进度
- ⏱️ 处理时间
- 📊 文件大小信息

🎯 仔细阅读日志，快速定位问题！🎯

## 📝 更新日志

### v1.1.0 🎉
- 🚀 **大文件处理优化**: 智能分页处理大文档，轻松处理8MB+文件！
- 🎯 **动态Token管理**: 根据文件大小自动调整token限制，性能提升！
- 📊 **增强错误处理**: 更完善的错误提示和重试机制！
- 🎨 **界面美化**: 添加更多颜表情，文档更生动！
- 📈 **性能优化**: 批量处理和内存管理优化！

### v1.0.0 🎊
- 🎉 初始版本发布
- 📄 支持PDF和Word文档转换
- 🤖 集成智谱AI API
- 📊 增强的表格处理功能
- 🔄 完善的重试机制
- 📦 批量处理功能

## 📜 许可证

本项目采用MIT许可证，自由使用，随意修改！🎉

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！🚀

### 🌟 如何贡献
1. 🍴 Fork 这个项目
2. 📝 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 💾 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 🚀 推送到分支 (`git push origin feature/AmazingFeature`)
5. 🔄 打开一个 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 🐙 提交GitHub Issue
- 📧 发送邮件至项目维护者
- 💬 在项目中留言讨论

---

## 🎉 最后

如果你觉得这个项目对你有帮助，请给个⭐️Star⭐️支持一下！🌟

你的支持是我们前进的动力！💪

**Made with ❤️ by Document Transformation Team**