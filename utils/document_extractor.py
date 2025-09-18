#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档抽取工具 - 支持从PDF和Word文件抽取内容
"""
import os
import yaml
import requests
from dotenv import load_dotenv

def read_api_key(config_path: str) -> str:
    """从配置文件中读取API密钥"""
    try:
        # 加载环境变量
        base_dir = os.path.dirname(os.path.dirname(__file__))
        dotenv_path = os.path.join(base_dir, '.env')
        load_dotenv(dotenv_path=dotenv_path)
        print(f"🔍 加载环境变量文件: {dotenv_path}")
        
        print(f"🔍 尝试读取配置文件: {config_path}")
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return ""
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            print(f"📋 配置文件内容: {config}")
        
        # 首先尝试从配置文件获取API密钥
        api_key = config.get("models", {}).get("glm-4.5v", {}).get("api_key", "")
        
        # 如果配置文件中是环境变量引用格式，尝试从环境变量获取
        if api_key and api_key.startswith('${') and api_key.endswith('}'):
            env_key = api_key[2:-1]  # 提取环境变量名
            api_key = os.getenv(env_key)
            print(f"🔍 从环境变量 {env_key} 获取API密钥")
            if api_key:
                print(f"✅ 成功从环境变量读取API密钥: {api_key[:10]}...{api_key[-4:]}")
            else:
                print(f"❌ 环境变量 {env_key} 中未找到API密钥")
        elif api_key:
            # 移除可能的引号
            api_key = api_key.strip('"\'')
            print(f"✅ 成功从配置文件读取API密钥: {api_key[:10]}...{api_key[-4:]}")
        else:
            print("❌ 配置文件中未找到API密钥")
        return api_key
    except Exception as e:
        print(f"❌ 读取API密钥失败: {e}")
        import traceback
        traceback.print_exc()
        return ""

def read_extraction_prompts(prompts_path: str) -> dict:
    """从YAML文件读取文档提取提示词"""
    try:
        print(f"🔍 读取提示词文件: {prompts_path}")
        if not os.path.exists(prompts_path):
            print(f"❌ 提示词文件不存在: {prompts_path}")
            return {}
        
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
            print(f"✅ 成功读取提示词: {list(prompts.keys())}")
            return prompts
    except Exception as e:
        print(f"❌ 读取提示词失败: {e}")
        return {}

def upload_file(file_path: str, api_key: str) -> str:
    """上传文件到GLM-4.5V服务器"""
    try:
        print(f"🔍 开始上传文件: {file_path}")
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return ""
        
        file_size = os.path.getsize(file_path)
        print(f"📁 文件大小: {file_size} bytes")
        
        url = "https://open.bigmodel.cn/api/paas/v4/files"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        file_name = os.path.basename(file_path)
        print(f"📄 文件名: {file_name}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            # 注意：对于文件上传，payload应该作为data参数传递，而不是单独的data
            data = {'purpose': 'file-extract'}
            print(f"🌐 发送请求到: {url}")
            print(f"📋 请求头: {headers}")
            print(f"📦 文件参数准备完成")
            
            # 增强重试机制
            max_retries = 3
            retry_delay = 5  # 秒
            for attempt in range(max_retries):
                try:
                    print(f"🔄 尝试 {attempt + 1}/{max_retries}")
                    response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
                    if response.status_code == 200:
                        break
                    else:
                        print(f"⚠️ 请求失败，状态码: {response.status_code}")
                        if attempt < max_retries - 1:
                            print(f"⏳ {retry_delay}秒后重试...")
                            import time
                            time.sleep(retry_delay)
                except requests.exceptions.RequestException as e:
                    print(f"❌ 第{attempt + 1}次请求失败: {e}")
                    if attempt < max_retries - 1:
                        print(f"⏳ {retry_delay}秒后重试...")
                        import time
                        time.sleep(retry_delay)
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 响应数据: {data}")
                # 根据参考代码，响应中的字段是"id"而不是"file_id"
                file_id = data.get("id", "")
                if file_id:
                    print(f"🎯 文件上传成功，文件ID: {file_id}")
                else:
                    print("❌ 响应中未找到id")
                return file_id
            else:
                print(f"❌ 服务器响应错误: {response.text}")
                raise Exception(f"文件上传失败: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return ""
    except requests.exceptions.ConnectionError:
        print("❌ 网络连接错误")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return ""
    except Exception as e:
        print(f"❌ 文件上传步骤失败: {e}")
        import traceback
        traceback.print_exc()
        return ""

def extract_content_from_file(file_path: str, file_type: str) -> str:
    """
    通用文档内容抽取函数
    
    Args:
        file_path: 文件路径
        file_type: 文件类型 (pdf, docx, doc)
    
    Returns:
        提取的文本内容
    """
    # 检查文件大小，决定是否需要分页处理
    file_size = os.path.getsize(file_path)
    print(f"📊 文件大小: {file_size} bytes")
    
    if file_size > 10 * 1024 * 1024:  # 大于10MB的文件使用分页处理
        print("📄 文件较大，使用分页处理")
        return extract_content_large_file(file_path, file_type)
    else:
        print("📄 文件较小，使用常规处理")
        return extract_content_normal_file(file_path, file_type)

def extract_content_normal_file(file_path: str, file_type: str) -> str:
    """
    常规文档内容抽取函数（适用于小文件）
    
    Args:
        file_path: 文件路径
        file_type: 文件类型 (pdf, docx, doc)
    
    Returns:
        提取的文本内容
    """
    try:
        file_type_name = {
            "pdf": "PDF",
            "docx": "Word(.docx)",
            "doc": "Word(.doc)"
        }.get(file_type, "未知")
        
        print(f"\n🚀 === 开始{file_type_name}内容抽取 ===")
        print(f"📁 输入文件: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ {file_type_name}文件未找到: {file_path}")
            raise FileNotFoundError(f"{file_type_name}文件未找到: {file_path}")
        
        # 读取API密钥
        print("🔑 步骤1: 读取API密钥")
        api_key = read_api_key("config/model_config.yaml")
        if not api_key:
            print("❌ API密钥未找到")
            raise Exception("API密钥未找到")
        
        # 上传文件
        print("📤 步骤2: 上传文件到GLM服务器")
        file_id = upload_file(file_path, api_key)
        if not file_id:
            print("❌ 文件上传失败")
            raise Exception("文件上传失败")
        
        # 调用 GLM-4.5V 模型的 API
        print("🤖 步骤3: 调用GLM-4.5V模型进行内容提取")
        
        # 读取YAML提示词
        prompts_path = "prompts/document_extraction_prompts.yaml"
        prompts = read_extraction_prompts(prompts_path)
        
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 使用统一的文档提取提示词
        prompt_key = "document_extraction_prompt"
        if prompt_key in prompts:
            prompt_template = prompts[prompt_key]
            # 先获取文件内容，然后将其包含在提示词中
            file_content_url = f"https://open.bigmodel.cn/api/paas/v4/files/{file_id}/content"
            print(f"🌐 获取文件内容用于处理: {file_content_url}")
            
            # 增强文件内容获取的重试机制
            max_retries = 3
            retry_delay = 5
            file_response = None
            for attempt in range(max_retries):
                try:
                    print(f"🔄 获取文件内容尝试 {attempt + 1}/{max_retries}")
                    file_response = requests.get(file_content_url, headers=headers, timeout=300)  # 增加超时时间到5分钟
                    if file_response.status_code == 200:
                        break
                    else:
                        print(f"⚠️ 获取文件内容失败，状态码: {file_response.status_code}")
                        if attempt < max_retries - 1:
                            print(f"⏳ {retry_delay}秒后重试...")
                            import time
                            time.sleep(retry_delay)
                except requests.exceptions.RequestException as e:
                    print(f"❌ 获取文件内容第{attempt + 1}次尝试失败: {e}")
                    if attempt < max_retries - 1:
                        print(f"⏳ {retry_delay}秒后重试...")
                        import time
                        time.sleep(retry_delay)
            
            if file_response and file_response.status_code == 200:
                file_data = file_response.json()
                raw_content = file_data.get("content", "")
                print(f"📝 获取到文件内容，长度: {len(raw_content)} 字符")
                
                # 将文件内容包含在提示词中
                content = prompt_template.format(
                    file_content=raw_content
                )
            else:
                print(f"❌ 获取文件内容失败: {file_response.text if file_response else '无响应'}")
                content = prompt_template.format(
                    file_content="[文件内容获取失败，请尝试其他方式]"
                )
        else:
            # 如果YAML文件中没有找到对应的提示词，使用默认提示词
            content = f"请提取以下文档的内容：\n文件ID: {file_id}\n文件类型: {file_type_name}\n请返回提取信息后的Markdown文档。"
        
        # 使用GLM-4.5V的聊天完成API，结合提示词来处理内容
        print(f"🌐 使用聊天完成API处理文件内容")
        
        # 根据文件大小动态调整max_tokens
        file_size = os.path.getsize(file_path)
        if file_size > 5 * 1024 * 1024:  # 大于5MB的文件
            max_tokens = 16000
        elif file_size > 2 * 1024 * 1024:  # 大于2MB的文件
            max_tokens = 12000
        else:
            max_tokens = 8000
            
        print(f"📊 文件大小: {file_size} bytes, 设置max_tokens: {max_tokens}")
        
        payload = {
            "model": "glm-4.5v",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        # 增强聊天API的重试机制
        max_retries = 3
        retry_delay = 10  # 聊天API重试间隔稍长
        chat_response = None
        for attempt in range(max_retries):
            try:
                print(f"🔄 聊天API尝试 {attempt + 1}/{max_retries}")
                chat_response = requests.post(url, headers=headers, json=payload, timeout=300)  # 增加超时时间到5分钟
                print(f"📊 聊天完成API响应状态码: {chat_response.status_code}")
                if chat_response.status_code == 200:
                    break
                else:
                    print(f"⚠️ 聊天API失败，状态码: {chat_response.status_code}")
                    if attempt < max_retries - 1:
                        print(f"⏳ {retry_delay}秒后重试...")
                        import time
                        time.sleep(retry_delay)
            except requests.exceptions.RequestException as e:
                print(f"❌ 聊天API第{attempt + 1}次尝试失败: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ {retry_delay}秒后重试...")
                    import time
                    time.sleep(retry_delay)
        
        if chat_response and chat_response.status_code == 200:
            chat_data = chat_response.json()
            print(f"✅ 聊天完成API响应数据: {chat_data}")
            
            # 获取处理后的内容
            processed_content = chat_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if processed_content:
                print(f"📝 成功处理文件内容，长度: {len(processed_content)} 字符")
                print(f"📄 内容预览: {processed_content[:200]}...")
                
                # 处理图片：如果文档中有图片，尝试提取并插入到相应位置
                processed_content = _process_images_in_content(processed_content, file_id, api_key, headers)
                
                return processed_content
            else:
                print("❌ 聊天完成API响应中未找到内容")
                print(f"完整响应: {chat_data}")
                return ""
        else:
            print(f"❌ 聊天完成API调用失败: {chat_response.text if chat_response else '无响应'}")
            # 如果聊天API失败，回退到文件内容API
            print("🔄 回退到文件内容API...")
            file_content_url = f"https://open.bigmodel.cn/api/paas/v4/files/{file_id}/content"
            print(f"🌐 文件内容API URL: {file_content_url}")
            
            # 再次尝试获取文件内容，使用增强的重试机制
            max_retries = 3
            retry_delay = 5
            fallback_file_response = None
            for attempt in range(max_retries):
                try:
                    print(f"🔄 回退获取文件内容尝试 {attempt + 1}/{max_retries}")
                    fallback_file_response = requests.get(file_content_url, headers=headers, timeout=300)
                    print(f"📊 回退文件内容响应状态码: {fallback_file_response.status_code}")
                    if fallback_file_response.status_code == 200:
                        file_response = fallback_file_response
                        break
                    else:
                        print(f"⚠️ 回退获取文件内容失败，状态码: {fallback_file_response.status_code}")
                        if attempt < max_retries - 1:
                            print(f"⏳ {retry_delay}秒后重试...")
                            import time
                            time.sleep(retry_delay)
                except requests.exceptions.RequestException as e:
                    print(f"❌ 回退获取文件内容第{attempt + 1}次尝试失败: {e}")
                    if attempt < max_retries - 1:
                        print(f"⏳ {retry_delay}秒后重试...")
                        import time
                        time.sleep(retry_delay)
            
            if fallback_file_response and fallback_file_response.status_code == 200:
                file_data = fallback_file_response.json()
                print(f"✅ 文件内容响应数据: {file_data}")
                
                # 获取文件内容
                file_content = file_data.get("content", "")
                if file_content:
                    print(f"📝 成功获取文件内容，长度: {len(file_content)} 字符")
                    print(f"📄 内容预览: {file_content[:200]}...")
                    return file_content
                else:
                    print("❌ 文件内容响应中未找到content")
                    print(f"完整响应: {file_data}")
                    return ""
            else:
                print(f"❌ 文件内容API调用失败: {fallback_file_response.text if fallback_file_response else '无响应'}")
                return ""
    except Exception as e:
        file_type_name = {
            "pdf": "PDF",
            "docx": "Word(.docx)",
            "doc": "Word(.doc)"
        }.get(file_type, "未知")
        print(f"❌ {file_type_name}内容抽取步骤失败: {e}")
        import traceback
        traceback.print_exc()
        return ""

def _process_images_in_content(content: str, file_id: str, api_key: str, headers: dict) -> str:
    """
    处理内容中的图片，将图片引用转换为实际的Markdown图片语法
    
    Args:
        content: 原始内容
        file_id: 文件ID
        api_key: API密钥
        headers: 请求头
    
    Returns:
        处理后的内容
    """
    try:
        # 检查内容中是否有图片引用
        if "![图片描述]" in content or "图片" in content:
            print("🖼️ 检测到内容中可能包含图片，尝试提取图片信息...")
            
            # 使用GLM-4.5V分析内容中的图片
            image_analysis_prompt = f"""
请分析以下文档内容，识别并提取所有图片信息：

**文档内容：**
{content}

**任务要求：**
1. 识别文档中所有图片的位置和描述
2. 为每个图片生成合适的标题和描述
3. 如果图片包含文字，请提取图片中的文字内容
4. 返回格式化的Markdown图片语法

**输出格式：**
请按照以下格式返回图片信息：
![图片标题](图片描述)
图片文字内容（如果有）：

请开始分析并返回图片信息。
"""
            
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            payload = {
                "model": "glm-4.5v",
                "messages": [
                    {
                        "role": "user",
                        "content": image_analysis_prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            # 增强图片分析API的重试机制
            max_retries = 2
            retry_delay = 5
            image_response = None
            for attempt in range(max_retries):
                try:
                    print(f"🔄 图片分析API尝试 {attempt + 1}/{max_retries}")
                    image_response = requests.post(url, headers=headers, json=payload, timeout=120)
                    if image_response.status_code == 200:
                        break
                    else:
                        print(f"⚠️ 图片分析API失败，状态码: {image_response.status_code}")
                        if attempt < max_retries - 1:
                            print(f"⏳ {retry_delay}秒后重试...")
                            import time
                            time.sleep(retry_delay)
                except requests.exceptions.RequestException as e:
                    print(f"❌ 图片分析API第{attempt + 1}次尝试失败: {e}")
                    if attempt < max_retries - 1:
                        print(f"⏳ {retry_delay}秒后重试...")
                        import time
                        time.sleep(retry_delay)
            
            if image_response and image_response.status_code == 200:
                image_data = image_response.json()
                image_content = image_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if image_content and "![图片" in image_content:
                    print(f"✅ 成功提取图片信息，长度: {len(image_content)} 字符")
                    
                    # 将图片信息插入到原始内容中的相应位置
                    # 这里简化处理，将图片信息添加到内容末尾
                    content += "\n\n---\n\n## 图片内容\n\n" + image_content
                else:
                    print("⚠️ 未检测到有效的图片信息")
            else:
                print(f"❌ 图片分析失败: {image_response.text if image_response else '无响应'}")
        
        return content
    except Exception as e:
        print(f"❌ 图片处理失败: {e}")
        return content

# 为了保持向后兼容，保留原有的函数名
def extract_content_from_pdf(pdf_path: str) -> str:
    """从PDF文件抽取内容"""
    return extract_content_from_file(pdf_path, "pdf")

def extract_content_from_docx(docx_path: str) -> str:
    """从Word文件抽取内容"""
    return extract_content_from_file(docx_path, "docx")

def extract_content_from_doc(doc_path: str) -> str:
    """从Word文件抽取内容"""
    return extract_content_from_file(doc_path, "doc")

def extract_content_large_file(file_path: str, file_type: str) -> str:
    """
    大文件内容抽取函数（适用于>10MB的文件）
    
    Args:
        file_path: 文件路径
        file_type: 文件类型 (pdf, docx, doc)
    
    Returns:
        提取的文本内容
    """
    try:
        file_type_name = {
            "pdf": "PDF",
            "docx": "Word(.docx)",
            "doc": "Word(.doc)"
        }.get(file_type, "未知")
        
        print(f"\n🚀 === 开始{file_type_name}大文件内容抽取 ===")
        print(f"📁 输入文件: {file_path}")
        print(f"📊 文件大小: {os.path.getsize(file_path)} bytes")
        
        if not os.path.exists(file_path):
            print(f"❌ {file_type_name}文件未找到: {file_path}")
            raise FileNotFoundError(f"{file_type_name}文件未找到: {file_path}")
        
        # 读取API密钥
        print("🔑 步骤1: 读取API密钥")
        api_key = read_api_key("config/model_config.yaml")
        if not api_key:
            print("❌ API密钥未找到")
            raise Exception("API密钥未找到")
        
        # 上传文件
        print("📤 步骤2: 上传文件到GLM服务器")
        file_id = upload_file(file_path, api_key)
        if not file_id:
            print("❌ 文件上传失败")
            raise Exception("文件上传失败")
        
        # 获取文件内容
        print("📄 步骤3: 获取文件内容")
        file_content_url = f"https://open.bigmodel.cn/api/paas/v4/files/{file_id}/content"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        # 获取文件内容
        max_retries = 3
        retry_delay = 5
        file_response = None
        for attempt in range(max_retries):
            try:
                print(f"🔄 获取文件内容尝试 {attempt + 1}/{max_retries}")
                file_response = requests.get(file_content_url, headers=headers, timeout=300)
                if file_response.status_code == 200:
                    break
                else:
                    print(f"⚠️ 获取文件内容失败，状态码: {file_response.status_code}")
                    if attempt < max_retries - 1:
                        print(f"⏳ {retry_delay}秒后重试...")
                        import time
                        time.sleep(retry_delay)
            except requests.exceptions.RequestException as e:
                print(f"❌ 获取文件内容第{attempt + 1}次尝试失败: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ {retry_delay}秒后重试...")
                    import time
                    time.sleep(retry_delay)
        
        if file_response and file_response.status_code == 200:
            file_data = file_response.json()
            raw_content = file_data.get("content", "")
            print(f"📝 获取到文件内容，长度: {len(raw_content)} 字符")
            
            if not raw_content:
                print("❌ 文件内容为空")
                return ""
            
            # 分块处理内容
            print("🔧 步骤4: 分块处理大文件内容")
            return process_content_in_chunks(raw_content, file_type_name, api_key)
        else:
            print(f"❌ 获取文件内容失败: {file_response.text if file_response else '无响应'}")
            return ""
            
    except Exception as e:
        print(f"❌ {file_type_name}大文件内容抽取步骤失败: {e}")
        import traceback
        traceback.print_exc()
        return ""

def process_content_in_chunks(content: str, file_type_name: str, api_key: str) -> str:
    """
    将大文件内容分块处理
    
    Args:
        content: 原始文件内容
        file_type_name: 文件类型名称
        api_key: API密钥
    
    Returns:
        处理后的完整内容
    """
    try:
        # 根据内容长度决定分块大小
        content_length = len(content)
        print(f"📊 原始内容长度: {content_length} 字符")
        
        # 设置分块大小（字符数）
        if content_length > 50000:  # 超过5万字符
            chunk_size = 15000  # 每块1.5万字符
        elif content_length > 20000:  # 超过2万字符
            chunk_size = 10000  # 每块1万字符
        else:
            chunk_size = 8000   # 每块8000字符
            
        print(f"🔧 设置分块大小: {chunk_size} 字符")
        
        # 计算需要分多少块
        num_chunks = (content_length + chunk_size - 1) // chunk_size
        print(f"📦 将分 {num_chunks} 块处理")
        
        processed_chunks = []
        
        # 逐块处理
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, content_length)
            chunk_content = content[start_idx:end_idx]
            
            print(f"🔄 处理第 {i + 1}/{num_chunks} 块 (字符 {start_idx}-{end_idx})")
            
            # 处理单个块
            processed_chunk = process_single_chunk(chunk_content, file_type_name, api_key)
            if processed_chunk:
                processed_chunks.append(processed_chunk)
                print(f"✅ 第 {i + 1} 块处理完成，长度: {len(processed_chunk)} 字符")
            else:
                print(f"⚠️ 第 {i + 1} 块处理失败，使用原始内容")
                processed_chunks.append(chunk_content)
        
        # 合并所有处理后的块
        if len(processed_chunks) == 1:
            final_content = processed_chunks[0]
        else:
            # 多块内容合并，添加分隔符
            final_content = "\n\n---\n\n".join(processed_chunks)
            # 添加分块处理说明
            final_content = f"""# {file_type_name}文档内容（分块处理）

> **说明**: 由于文档较大，已自动分块处理。各部分内容之间用 `---` 分隔。

{final_content}

---

# 文档结束
"""
        
        print(f"🎉 大文件处理完成，最终内容长度: {len(final_content)} 字符")
        return final_content
        
    except Exception as e:
        print(f"❌ 分块处理失败: {e}")
        import traceback
        traceback.print_exc()
        return content  # 返回原始内容作为回退

def process_single_chunk(chunk_content: str, file_type_name: str, api_key: str) -> str:
    """
    处理单个内容块
    
    Args:
        chunk_content: 单个块的内容
        file_type_name: 文件类型名称
        api_key: API密钥
    
    Returns:
        处理后的块内容
    """
    try:
        # 读取YAML提示词
        prompts_path = "prompts/document_extraction_prompts.yaml"
        prompts = read_extraction_prompts(prompts_path)
        
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 使用统一的文档提取提示词
        prompt_key = "document_extraction_prompt"
        if prompt_key in prompts:
            prompt_template = prompts[prompt_key]
            # 将块内容包含在提示词中
            content = prompt_template.format(
                file_content=chunk_content
            )
        else:
            # 如果YAML文件中没有找到对应的提示词，使用默认提示词
            content = f"""请提取以下文档片段的内容：

**文档片段：**
{chunk_content}

**文件类型：** {file_type_name}

**任务要求：**
1. 提取关键信息和结构化内容
2. 保持原文的逻辑结构
3. 生成清晰的Markdown格式
4. 如果这是大文档的一部分，请确保内容连贯性

请开始处理。"""
        
        # 设置块处理的token限制
        max_tokens = min(6000, len(chunk_content) // 2)  # 根据块大小动态调整
        
        payload = {
            "model": "glm-4.5v",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        print(f"📊 块内容长度: {len(chunk_content)} 字符，设置max_tokens: {max_tokens}")
        
        # 发送请求处理块内容
        max_retries = 2
        retry_delay = 5
        chunk_response = None
        for attempt in range(max_retries):
            try:
                print(f"🔄 块处理API尝试 {attempt + 1}/{max_retries}")
                chunk_response = requests.post(url, headers=headers, json=payload, timeout=120)
                if chunk_response.status_code == 200:
                    break
                else:
                    print(f"⚠️ 块处理API失败，状态码: {chunk_response.status_code}")
                    if attempt < max_retries - 1:
                        print(f"⏳ {retry_delay}秒后重试...")
                        import time
                        time.sleep(retry_delay)
            except requests.exceptions.RequestException as e:
                print(f"❌ 块处理API第{attempt + 1}次尝试失败: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ {retry_delay}秒后重试...")
                    import time
                    time.sleep(retry_delay)
        
        if chunk_response and chunk_response.status_code == 200:
            chunk_data = chunk_response.json()
            processed_chunk = chunk_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if processed_chunk:
                print(f"✅ 块内容处理成功，长度: {len(processed_chunk)} 字符")
                return processed_chunk
            else:
                print("❌ 块内容处理结果为空")
                return chunk_content  # 返回原始内容
        else:
            print(f"❌ 块内容处理失败: {chunk_response.text if chunk_response else '无响应'}")
            return chunk_content  # 返回原始内容
            
    except Exception as e:
        print(f"❌ 单块处理失败: {e}")
        return chunk_content  # 返回原始内容作为回退