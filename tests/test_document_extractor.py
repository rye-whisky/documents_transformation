#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档抽取器测试 - 独立版本
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.document_extractor import (
    extract_content_from_pdf,
    extract_content_from_docx,
    upload_file,
    read_api_key,
    read_extraction_prompts
)

class TestDocumentExtractor(unittest.TestCase):
    """文档抽取器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_pdf_path = "test.pdf"
        self.test_docx_path = "test.docx"
        self.config_path = "config/model_config.yaml"
        self.prompts_path = "prompts/document_extraction_prompts.yaml"
        
        # 创建测试文件
        with open(self.test_pdf_path, 'w') as f:
            f.write("测试PDF内容")
        with open(self.test_docx_path, 'w') as f:
            f.write("测试Word内容")
    
    def tearDown(self):
        """测试后清理"""
        # 删除测试文件
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)
        if os.path.exists(self.test_docx_path):
            os.remove(self.test_docx_path)
    
    @patch('utils.document_extractor.extract_content_from_file')
    def test_extract_content_from_pdf(self, mock_extract):
        """测试PDF内容抽取"""
        mock_extract.return_value = "测试PDF提取结果"
        
        result = extract_content_from_pdf(self.test_pdf_path)
        self.assertEqual(result, "测试PDF提取结果")
        mock_extract.assert_called_once_with(self.test_pdf_path, "pdf")
    
    @patch('utils.document_extractor.extract_content_from_file')
    def test_extract_content_from_docx(self, mock_extract):
        """测试Word内容抽取"""
        mock_extract.return_value = "测试Word提取结果"
        
        result = extract_content_from_docx(self.test_docx_path)
        self.assertEqual(result, "测试Word提取结果")
        mock_extract.assert_called_once_with(self.test_docx_path, "docx")
    
    @patch('utils.document_extractor.requests.post')
    def test_upload_file_success(self, mock_post):
        """测试文件上传成功"""
        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_file_id"}
        mock_post.return_value = mock_response
        
        result = upload_file(self.test_pdf_path, "test_api_key")
        self.assertEqual(result, "test_file_id")
    
    @patch('utils.document_extractor.os.path.exists')
    @patch('utils.document_extractor.yaml.safe_load')
    def test_read_api_key_file_exists(self, mock_yaml, mock_exists):
        """测试读取存在的API密钥文件"""
        mock_exists.return_value = True
        mock_yaml.return_value = {"glm-4.5v": {"api_key": "test_key"}}
        
        result = read_api_key(self.config_path)
        self.assertEqual(result, "test_key")
    
    @patch('utils.document_extractor.os.path.exists')
    def test_read_api_key_file_not_exists(self, mock_exists):
        """测试读取不存在的API密钥文件"""
        mock_exists.return_value = False
        
        result = read_api_key(self.config_path)
        self.assertEqual(result, "")
    
    @patch('utils.document_extractor.os.path.exists')
    @patch('utils.document_extractor.yaml.safe_load')
    def test_read_extraction_prompts(self, mock_yaml, mock_exists):
        """测试读取提取提示词"""
        mock_exists.return_value = True
        mock_yaml.return_value = {"document_extraction_prompt": "test_prompt"}
        
        result = read_extraction_prompts(self.prompts_path)
        self.assertEqual(result, {"document_extraction_prompt": "test_prompt"})

if __name__ == '__main__':
    unittest.main()