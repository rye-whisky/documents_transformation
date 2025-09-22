#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLM文件管理器 - 管理GLM-4.5V服务器的文件操作
"""
import os
import requests
import yaml
from typing import Dict, List, Optional, Any


class GLMFileManager:
    """GLM文件管理器类"""
    
    def __init__(self, api_key: str):
        """
        初始化GLM文件管理器
        
        Args:
            api_key: GLM API密钥
        """
        self.api_key = api_key
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }
    
    def get_file_list(self, limit: int = 20, purpose: str = "file-extract") -> List[Dict[str, Any]]:
        """
        获取文件列表
        
        Args:
            limit: 返回文件数量限制，默认20
            purpose: 文件用途，默认为file-extract
        
        Returns:
            文件列表，每个文件包含id、filename、bytes、created_at、purpose等信息
        """
        try:
            print(f"🔍 获取文件列表，限制数量: {limit}, 用途: {purpose}")
            
            url = f"{self.base_url}/files"
            params = {
                "limit": str(limit),
                "purpose": purpose
            }
            
            print(f"🌐 请求URL: {url}")
            print(f"📋 请求参数: {params}")
            
            response = requests.get(url, headers=self.headers, params=params)
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取文件列表")
                
                # 根据GLM API文档，文件列表在data字段中
                files = data.get("data", [])
                print(f"📁 找到 {len(files)} 个文件")
                
                # 打印文件信息
                for file_info in files:
                    print(f"📄 文件ID: {file_info.get('id')}, "
                          f"文件名: {file_info.get('filename')}, "
                          f"大小: {file_info.get('bytes')} bytes, "
                          f"创建时间: {file_info.get('created_at')}")
                
                return files
            else:
                print(f"❌ 获取文件列表失败: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return []
        except Exception as e:
            print(f"❌ 获取文件列表步骤失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        获取特定文件的详细信息
        
        Args:
            file_id: 文件ID
        
        Returns:
            文件详细信息，如果失败返回None
        """
        try:
            print(f"🔍 获取文件信息，文件ID: {file_id}")
            
            url = f"{self.base_url}/files/{file_id}"
            
            response = requests.get(url, headers=self.headers)
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取文件信息: {data}")
                return data
            else:
                print(f"❌ 获取文件信息失败: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return None
        except Exception as e:
            print(f"❌ 获取文件信息步骤失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        删除文件
        
        Args:
            file_id: 文件ID
        
        Returns:
            删除成功返回True，失败返回False
        """
        try:
            print(f"🗑️ 删除文件，文件ID: {file_id}")
            
            url = f"{self.base_url}/files/{file_id}"
            
            response = requests.delete(url, headers=self.headers)
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 文件删除成功")
                return True
            else:
                print(f"❌ 文件删除失败: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False
        except Exception as e:
            print(f"❌ 删除文件步骤失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_all_files(self, purpose: str = "file-extract", batch_size: int = 10, require_confirmation: bool = True) -> Dict[str, Any]:
        """
        删除所有上传的文件
        
        Args:
            purpose: 文件用途，默认为file-extract
            batch_size: 批量删除的大小，默认为10
            require_confirmation: 是否需要用户确认，默认为True
        
        Returns:
            删除结果统计，包含成功和失败的文件数量
        """
        try:
            # 如果需要用户确认
            if require_confirmation:
                print("\n🗑️ 是否要删除所有文件？此操作不可恢复！")
                user_input = input("请输入 yes/Y 确认删除，或其他键跳过: ")
                if user_input.lower() not in ['yes', 'y']:
                    print("\n⏭️ 跳过删除文件操作")
                    return {"total": 0, "success": 0, "failed": 0, "failed_files": [], "skipped": True}
            
            print(f"🗑️ 开始删除所有上传的文件，用途: {purpose}")
            
            # 获取所有文件
            files = self.get_file_list(limit=1000, purpose=purpose)  # 获取大量文件
            
            if not files:
                print("ℹ️ 没有找到需要删除的文件")
                return {"total": 0, "success": 0, "failed": 0, "failed_files": []}
            
            total_files = len(files)
            print(f"📁 找到 {total_files} 个文件需要删除")
            
            # 统计结果
            result = {
                "total": total_files,
                "success": 0,
                "failed": 0,
                "failed_files": []
            }
            
            # 批量删除文件
            for i in range(0, total_files, batch_size):
                batch = files[i:i + batch_size]
                print(f"\n📦 删除批次 {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size}")
                
                for file_info in batch:
                    file_id = file_info.get('id')
                    filename = file_info.get('filename', 'unknown')
                    
                    print(f"🗑️ 删除文件: {filename} (ID: {file_id})")
                    
                    if self.delete_file(file_id):
                        result["success"] += 1
                        print(f"✅ 文件删除成功: {filename}")
                    else:
                        result["failed"] += 1
                        result["failed_files"].append({
                            "file_id": file_id,
                            "filename": filename
                        })
                        print(f"❌ 文件删除失败: {filename}")
                    
                    # 添加短暂延迟，避免请求过于频繁
                    import time
                    time.sleep(0.1)
            
            print(f"\n📊 删除完成统计:")
            print(f"   总文件数: {result['total']}")
            print(f"   删除成功: {result['success']}")
            print(f"   删除失败: {result['failed']}")
            
            if result["failed_files"]:
                print(f"   失败文件列表:")
                for failed_file in result["failed_files"]:
                    print(f"     - {failed_file['filename']} (ID: {failed_file['file_id']})")
            
            return result
            
        except Exception as e:
            print(f"❌ 删除所有文件步骤失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "failed_files": [],
                "error": str(e)
            }
    
    def upload_file(self, file_path: str, purpose: str = "file-extract") -> Optional[str]:
        """
        上传文件到GLM服务器
        
        Args:
            file_path: 本地文件路径
            purpose: 文件用途，默认为file-extract
        
        Returns:
            上传成功返回文件ID，失败返回None
        """
        try:
            print(f"📤 上传文件: {file_path}")
            
            if not os.path.exists(file_path):
                print(f"❌ 文件不存在: {file_path}")
                return None
            
            file_size = os.path.getsize(file_path)
            print(f"📁 文件大小: {file_size} bytes")
            
            url = f"{self.base_url}/files"
            file_name = os.path.basename(file_path)
            print(f"📄 文件名: {file_name}")
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f)}
                data = {'purpose': purpose}
                
                print(f"🌐 发送请求到: {url}")
                
                # 增强重试机制
                max_retries = 3
                retry_delay = 5  # 秒
                for attempt in range(max_retries):
                    try:
                        print(f"🔄 尝试 {attempt + 1}/{max_retries}")
                        response = requests.post(url, headers=self.headers, files=files, data=data, timeout=60)
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
                    file_id = data.get("id", "")
                    if file_id:
                        print(f"🎯 文件上传成功，文件ID: {file_id}")
                        return file_id
                    else:
                        print("❌ 响应中未找到id")
                        return None
                else:
                    print(f"❌ 服务器响应错误: {response.text}")
                    return None
                    
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ 网络连接错误")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return None
        except Exception as e:
            print(f"❌ 文件上传步骤失败: {e}")
            import traceback
            traceback.print_exc()
            return None


def get_file_list_example(api_key: str, limit: int = 20, purpose: str = "file-extract") -> List[Dict[str, Any]]:
    """
    获取文件列表示例函数
    
    Args:
        api_key: GLM API密钥
        limit: 返回文件数量限制，默认20
        purpose: 文件用途，默认为file-extract
    
    Returns:
        文件列表
    """
    file_manager = GLMFileManager(api_key)
    return file_manager.get_file_list(limit, purpose)


def load_api_key() -> str:
    """
    从多个来源加载API密钥
    
    Returns:
        API密钥字符串
    """
    # 1. 首先尝试从环境变量获取
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if api_key:
        print("✅ 从环境变量加载API密钥")
        return api_key
    
    # 2. 尝试从.env文件加载
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if api_key:
            print("✅ 从.env文件加载API密钥")
            return api_key
    except ImportError:
        print("⚠️ 未安装python-dotenv库，跳过.env文件加载")
    
    # 3. 尝试从配置文件加载
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "model_config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            # 尝试从glm-4.5v配置获取API密钥
            if 'models' in config and 'glm-4.5v' in config['models']:
                api_key = config['models']['glm-4.5v'].get('api_key')
                if api_key:
                    print("✅ 从配置文件(glm-4.5v)加载API密钥")
                    return api_key
            # 尝试从glm-4.5-air配置获取API密钥
            if 'models' in config and 'glm-4.5-air' in config['models']:
                api_key = config['models']['glm-4.5-air'].get('api_key')
                if api_key:
                    print("✅ 从配置文件(glm-4.5-air)加载API密钥")
                    return api_key
    except Exception as e:
        print(f"⚠️ 从配置文件加载API密钥失败: {e}")
    
    return None


if __name__ == "__main__":
    # 示例用法
    print("🚀 === GLM文件管理器示例 ===")
    print("正在尝试从多个来源加载API密钥...")
    
    # 加载API密钥
    api_key = load_api_key()
    
    if not api_key:
        print("❌ 未找到API密钥")
        print("请通过以下方式之一设置API密钥：")
        print("1. 设置环境变量: export ZHIPUAI_API_KEY=your_api_key")
        print("2. 创建.env文件并添加: ZHIPUAI_API_KEY=your_api_key")
        print("3. 在config/model_config.yaml中配置API密钥")
        exit(1)
    
    # 创建文件管理器实例
    file_manager = GLMFileManager(api_key)
    
    # 获取文件列表
    print("\n📋 获取文件列表:")
    files = file_manager.get_file_list(limit=10)
    
    if files:
        print(f"\n✅ 成功获取 {len(files)} 个文件")
        for i, file_info in enumerate(files, 1):
            print(f"{i}. ID: {file_info.get('id')}")
            print(f"   文件名: {file_info.get('filename')}")
            print(f"   大小: {file_info.get('bytes')} bytes")
            print(f"   创建时间: {file_info.get('created_at')}")
            print(f"   用途: {file_info.get('purpose')}")
            print("---")
    else:
        print("❌ 未获取到文件列表")
    
    # 删除所有文件（函数内部会提示用户确认）
    result = file_manager.delete_all_files("file-extract", 10)
    if result.get("skipped"):
        print("操作已跳过")
    else:
        print(f"删除结果: {result}")