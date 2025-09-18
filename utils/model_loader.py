#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型加载器
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import yaml

def get_glm_instance(model_type: str) -> ChatOpenAI:
    """根据配置文件和环境变量，以及指定的模型类型，创建并返回一个GLM实例"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dotenv_path = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path=dotenv_path)

    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'model_config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    model_config = config.get('models', {}).get(model_type)
    
    if model_config is None:
        raise ValueError(f"错误: 在 model_config.yaml 中未找到 '{model_type}' 的配置。")

    provider = model_config.get("provider")
    
    llm = None

    if provider == "zhipu":
        api_key = model_config.get("api_key", os.getenv("ZHIPUAI_API_KEY"))
        if not api_key:
            raise ValueError("错误: ZHIPUAI_API_KEY 环境变量未设置或api_key未在配置中提供。")
        
        llm = ChatOpenAI(
            temperature=model_config.get("temperature", 0.7),
            model=model_config.get("model_name"),
            openai_api_key=api_key,
            openai_api_base=model_config.get("api_base")
        )

    if llm is None:
        raise ValueError(f"错误: 不支持的provider '{provider}' 或模型实例化失败。")
        
    return llm


def load_model(model_type: str = "glm-4.5-air") -> ChatOpenAI:
    """
    加载GLM-4.5-Air文本模型实例
    
    Args:
        model_type: 模型类型，默认为"glm-4.5-air"
        
    Returns:
        ChatOpenAI: GLM-4.5-Air模型实例
    """
    return get_glm_instance(model_type)

def load_multimodal_model() -> ChatOpenAI:
    """
    加载GLM-4.5V多模态模型实例
    
    Returns:
        ChatOpenAI: GLM-4.5V多模态模型实例
    """
    return get_glm_instance("glm-4.5v")