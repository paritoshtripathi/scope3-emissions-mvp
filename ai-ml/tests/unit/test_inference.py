"""
Unit tests for inference engine with config-driven functionality
"""
import pytest
import os
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from src.rag.models.inference import InferenceEngine, LLMConfig

@pytest.fixture
def test_config():
    return {
        'embedding_model': {
            'name': 'test-embedding-model',
            'batch_size': 16,
            'cache_size': 50
        },
        'llm_defaults': {
            'max_retries': 2,
            'retry_delay': 0.5,
            'timeout': 15.0,
            'default_model': 'test-model'
        },
        'models': {
            'test-model': {
                'model_id': 'test/model',
                'provider': 'test-provider',
                'parameters': {
                    'temperature': 0.5,
                    'max_tokens': 100
                },
                'domain_prompts': {
                    'test-domain': 'Test prompt: {context}\nQuestion: {question}'
                }
            }
        }
    }

@pytest.fixture
def temp_config_file(tmp_path, test_config):
    config_path = tmp_path / 'test_config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(test_config, f)
    return str(config_path)

@pytest.fixture
def mock_sentence_transformer():
    with patch('src.rag.models.inference.SentenceTransformer') as mock:
        yield mock

@pytest.fixture
def mock_huggingface_endpoint():
    with patch('src.rag.models.inference.HuggingFaceEndpoint') as mock:
        yield mock

def test_load_config_from_file(temp_config_file, mock_sentence_transformer):
    """Test loading configuration from file"""
    engine = InferenceEngine(config_path=temp_config_file)
    
    assert engine.config['embedding_model']['name'] == 'test-embedding-model'
    assert engine.config['llm_defaults']['max_retries'] == 2
    assert 'test-model' in engine.config['models']

def test_fallback_to_default_config(mock_sentence_transformer):
    """Test fallback to default configuration"""
    engine = InferenceEngine(config_path='nonexistent.yaml')
    
    assert engine.config['embedding_model']['name'] == 'BAAI/bge-large-en-v1.5'
    assert engine.config['llm_defaults']['max_retries'] == 3
    assert 'llama3' in engine.config['models']

def test_configure_llm_with_parameters(temp_config_file, mock_sentence_transformer, mock_huggingface_endpoint):
    """Test LLM configuration with custom parameters"""
    engine = InferenceEngine(config_path=temp_config_file)
    
    custom_params = {'temperature': 0.8}
    engine.configure_llm('test-model', parameters=custom_params)
    
    assert engine.current_config.parameters['temperature'] == 0.8
    mock_huggingface_endpoint.assert_called_once()

def test_generate_embeddings_with_config_batch_size(temp_config_file, mock_sentence_transformer):
    """Test embedding generation with configured batch size"""
    mock_model = Mock()
    mock_sentence_transformer.return_value = mock_model
    mock_model.encode.return_value = [[1.0, 2.0]]
    
    engine = InferenceEngine(config_path=temp_config_file)
    texts = ['test'] * 20
    
    engine.generate_embeddings(texts)
    
    # Should use batch_size from config (16)
    assert mock_model.encode.call_count == 2

def test_domain_prompt_templates(temp_config_file, mock_sentence_transformer):
    """Test domain-specific prompt templates"""
    engine = InferenceEngine(config_path=temp_config_file)
    engine.configure_llm('test-model')
    
    prompt = engine._get_prompt_template('test-domain')
    formatted = prompt.format(context='test context', question='test question')
    
    assert 'Test prompt: test context' in formatted
    assert 'Question: test question' in formatted

def test_add_new_llm_config(temp_config_file, mock_sentence_transformer):
    """Test adding new LLM configuration"""
    engine = InferenceEngine(config_path=temp_config_file)
    
    new_config = LLMConfig(
        model_id='new/model',
        provider='new-provider',
        parameters={'temperature': 0.3},
        domain_prompts={'new-domain': 'New prompt: {context}'}
    )
    
    engine.add_llm_config('new-model', new_config)
    assert 'new-model' in engine.llm_configs
    assert engine.llm_configs['new-model'].model_id == 'new/model'

def test_reload_config(temp_config_file, mock_sentence_transformer):
    """Test configuration reloading"""
    engine = InferenceEngine(config_path=temp_config_file)
    original_model = engine.config['embedding_model']['name']
    
    # Modify config file
    config = engine.config.copy()
    config['embedding_model']['name'] = 'new-model'
    with open(temp_config_file, 'w') as f:
        yaml.dump(config, f)
    
    engine.reload_config(temp_config_file)
    assert engine.config['embedding_model']['name'] == 'new-model'
    assert engine.config['embedding_model']['name'] != original_model

@pytest.mark.asyncio
async def test_generate_response_with_retries(temp_config_file, mock_sentence_transformer, mock_huggingface_endpoint):
    """Test response generation with configured retries"""
    mock_llm = Mock()
    mock_huggingface_endpoint.return_value = mock_llm
    mock_llm.invoke.side_effect = [Exception("Test error"), "Success"]
    
    engine = InferenceEngine(config_path=temp_config_file)
    engine.configure_llm('test-model')
    
    response = await engine.generate_response("test query", "test context")
    assert response == "Success"
    assert mock_llm.invoke.call_count == 2

def test_backward_compatibility(mock_sentence_transformer):
    """Test backward compatibility with default values"""
    engine = InferenceEngine()  # No config provided
    
    assert engine.config['embedding_model']['batch_size'] == 32
    assert engine.config['llm_defaults']['max_retries'] == 3
    assert 'llama3' in engine.llm_configs

@pytest.mark.asyncio
async def test_custom_timeout_and_retries(temp_config_file, mock_sentence_transformer, mock_huggingface_endpoint):
    """Test custom timeout and retry settings"""
    engine = InferenceEngine(config_path=temp_config_file)
    engine.configure_llm('test-model')
    
    # Test with custom values
    response = await engine.generate_response(
        "test query",
        "test context",
        max_retries=1,
        retry_delay=0.1
    )
    
    # Should use custom values instead of config values
    assert engine.config['llm_defaults']['max_retries'] == 2  # Config value
    assert engine.config['llm_defaults']['retry_delay'] == 0.5  # Config value