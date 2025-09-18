#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础工作流类
"""
import os
from abc import ABC, abstractmethod
from typing import Optional

class BaseWorkflow(ABC):
    """
    基础工作流抽象类
    
    所有具体的工作流都应该继承这个类并实现 run 方法
    """
    
    def __init__(self, base_dir: str, output_dir: str):
        """
        初始化工作流
        
        Args:
            base_dir: 基础目录，用于存放输入文件
            output_dir: 输出目录，用于存放处理结果
        """
        self.base_dir = base_dir
        self.output_dir = output_dir
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"🏗️ 基础工作流已初始化")
        print(f"📁 基础目录: {self.base_dir}")
        print(f"📤 输出目录: {self.output_dir}")
    
    @abstractmethod
    async def run(self, **kwargs) -> Optional[str]:
        """
        运行工作流的抽象方法
        
        Args:
            **kwargs: 工作流特定的参数
            
        Returns:
            处理结果，失败时返回 None
        """
        pass
    
    def _save_markdown(self, markdown_content: str, source_path: str, file_type: str) -> None:
        """保存Markdown内容到文件"""
        try:
            base_filename = os.path.splitext(os.path.basename(source_path))[0]
            output_filename = f"{base_filename}_extracted_content.md"
            output_path = os.path.join(self.output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Markdown内容已保存至: {output_path}")
        except Exception as e:
            print(f"❌ 保存Markdown内容失败: {e}")