#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理文件夹中的所有 PDF 和 Word 文档
"""
import os
import sys
import asyncio
from typing import List, Tuple

# 添加当前目录到Python路径，以便导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.unified_content_extraction_workflow import UnifiedContentExtractionWorkflow

def process_documents(input_dir, output_dir, batch_size: int = 3):
    """
    处理文件夹中的所有 PDF 和 Word 文档，支持批量处理
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        batch_size: 批量处理大小，默认为3
    """
    # 初始化工作流
    workflow = UnifiedContentExtractionWorkflow(base_dir=input_dir, output_dir=output_dir)
    
    # 收集所有文件
    pdf_files = []
    doc_files = []
    
    print(f"🔍 扫描输入目录: {input_dir}")
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if filename.lower().endswith('.pdf'):
            pdf_files.append(file_path)
        elif filename.lower().endswith(('.doc', '.docx')):
            doc_files.append(file_path)
    
    print(f"📁 找到 {len(pdf_files)} 个PDF文件")
    print(f"📄 找到 {len(doc_files)} 个Word文件")
    
    # 批量处理PDF文件
    if pdf_files:
        print(f"\n🚀 开始批量处理PDF文件 (批次大小: {batch_size})")
        for i in range(0, len(pdf_files), batch_size):
            batch = pdf_files[i:i + batch_size]
            print(f"\n📦 处理PDF批次 {i//batch_size + 1}/{(len(pdf_files) + batch_size - 1)//batch_size}")
            print(f"📋 批次文件: {[os.path.basename(f) for f in batch]}")
            
            for file_path in batch:
                try:
                    print(f"📄 处理: {os.path.basename(file_path)}")
                    asyncio.run(workflow.run_from_file(file_path, "pdf"))
                except Exception as e:
                    print(f"❌ 处理文件失败 {os.path.basename(file_path)}: {e}")
    
    # 批量处理Word文件
    if doc_files:
        print(f"\n🚀 开始批量处理Word文件 (批次大小: {batch_size})")
        for i in range(0, len(doc_files), batch_size):
            batch = doc_files[i:i + batch_size]
            print(f"\n📦 处理Word批次 {i//batch_size + 1}/{(len(doc_files) + batch_size - 1)//batch_size}")
            print(f"📋 批次文件: {[os.path.basename(f) for f in batch]}")
            
            for file_path in batch:
                try:
                    print(f"📄 处理: {os.path.basename(file_path)}")
                    asyncio.run(workflow.run_from_file(file_path, "docx"))
                except Exception as e:
                    print(f"❌ 处理文件失败 {os.path.basename(file_path)}: {e}")
    
    print(f"\n✅ 所有文件处理完成！")

if __name__ == "__main__":
    # 示例用法
    input_directory = r"input"  # 输入目录
    output_directory = r"output"  # 输出目录
    
    # 确保目录存在
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    
    process_documents(input_directory, output_directory)