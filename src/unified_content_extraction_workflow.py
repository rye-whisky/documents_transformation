#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一内容抽取工作流 - 支持从PDF和Word文件抽取内容
"""
import os
from typing import Optional, List, Dict
from datetime import datetime
import asyncio

# 尝试相对导入
try:
    from .base_workflow import BaseWorkflow
    from ..utils.document_extractor import extract_content_from_pdf, extract_content_from_docx
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from src.base_workflow import BaseWorkflow
    from utils.document_extractor import extract_content_from_pdf, extract_content_from_docx

class UnifiedContentExtractionWorkflow(BaseWorkflow):
    """
    统一内容抽取工作流 - 方案实现
    
    完整流程：
    1. PDF/Word内容抽取
    2. 内容转换为Markdown格式
    3. 传递内容给后续处理步骤
    """
    
    def __init__(self, base_dir: str, output_dir: str):
        super().__init__(base_dir, output_dir)
        self.loop = asyncio.get_event_loop()
        print("🚀 Unified Content Extraction Workflow 已初始化")
    
    async def run(self, **kwargs) -> Optional[str]:
        """
        统一入口方法，实现BaseWorkflow的抽象方法
        根据参数自动选择运行模式
        """
        # 检查是否有pdf_path或docx_path参数
        if 'pdf_path' in kwargs:
            return await self.run_from_file(kwargs['pdf_path'], "pdf")
        elif 'docx_path' in kwargs:
            return await self.run_from_file(kwargs['docx_path'], "docx")
        else:
            raise ValueError("必须提供 pdf_path 或 docx_path 参数")
    
    async def run_from_file(self, file_path: str, file_type: str) -> Optional[str]:
        """
        从文件运行内容抽取工作流（支持PDF和Word文档）
        
        Args:
            file_path: 输入文件路径
            file_type: 文件类型（"pdf" 或 "docx"）
            
        Returns:
            Markdown格式的内容，失败返回None
        """
        try:
            file_type_name = "PDF" if file_type == "pdf" else "Word"
            print(f"\n🚀 === {file_type_name}内容抽取 ===")
            print(f"📁 输入文件: {os.path.basename(file_path)}")
            print()
            
            # 步骤1: 内容抽取
            print(f"📋 [步骤1/2] {file_type_name}内容抽取")
            if file_type == "pdf":
                extraction_result = await self._extract_content_from_pdf(file_path)
            else:
                extraction_result = await self._extract_content_from_docx(file_path)
            
            if not extraction_result:
                return None
            
            # 步骤2: 内容转换为Markdown格式
            print("\n📝 [步骤2/2] 内容转换为Markdown格式")
            markdown_content = extraction_result
            
            if markdown_content:
                self._save_markdown(markdown_content, file_path, file_type)
                print(f"✅ {file_type_name}内容抽取与转换完成")
            else:
                return None
            return markdown_content
                
        except Exception as e:
            file_type_name = "PDF" if file_type == "pdf" else "Word"
            print(f"❌ {file_type_name}内容抽取与转换失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _extract_content_from_pdf(self, pdf_path: str) -> Optional[str]:
        """PDF内容抽取步骤"""
        return extract_content_from_pdf(pdf_path)
    
    async def _extract_content_from_docx(self, docx_path: str) -> Optional[str]:
        """Word内容抽取步骤"""
        return extract_content_from_docx(docx_path)