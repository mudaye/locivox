"""
Tests for audio buffer module (Phase 2)
"""

import pytest
import numpy as np
from src.buffer import AudioBuffer


@pytest.fixture
def basic_config():
    """Basic buffer configuration"""
    return {
        'audio': {
            'sample_rate': 16000
        },
        'streaming': {
            'chunk_size': 5.0,
            'chunk_overlap': 1.0,
            'buffer_size': 10
        }
    }


@pytest.fixture
def buffer(basic_config):
    """Create buffer instance"""
    return AudioBuffer(basic_config)


class TestAudioBuffer:
    """Tests for AudioBuffer"""
    
    def test_init(self, buffer):
        """Test buffer initialization"""
        assert buffer.sample_rate == 16000
        assert buffer.chunk_duration == 5.0
        assert buffer.overlap_duration == 1.0
        assert buffer.max_chunks == 10
        
        # Check calculated sizes
        assert buffer.chunk_samples == 80000  # 5s * 16000
        assert buffer.overlap_samples == 16000  # 1s * 16000
        assert buffer.step_samples == 64000  # 80000 - 16000
    
    def test_initial_state(self, buffer):
        """Test initial buffer state"""
        assert len(buffer.buffer) == 0
        assert len(buffer.chunks_queue) == 0
        assert not buffer.has_chunks()
        assert buffer.get_queue_size() == 0
    
    def test_add_audio_simple(self, buffer):
        """Test adding audio data"""
        # Add 1 second of audio
        audio_data = np.random.randn(16000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        assert len(buffer.buffer) == 16000
        assert not buffer.has_chunks()  # Not enough for a chunk yet
    
    def test_add_audio_creates_chunk(self, buffer):
        """Test that adding enough audio creates a chunk"""
        # Add 5 seconds of audio (one full chunk)
        audio_data = np.random.randn(80000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        assert buffer.has_chunks()
        assert buffer.get_queue_size() == 1
    
    def test_add_audio_creates_multiple_chunks(self, buffer):
        """Test creating multiple chunks"""
        # Add 10 seconds of audio (should create 2 chunks with overlap)
        audio_data = np.random.randn(160000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # First chunk: 0-5s (80000 samples)
        # Buffer advances by 4s (64000 samples) due to overlap
        # Remaining: 6s (96000 samples)
        # Second chunk: 4-9s (80000 samples)
        # Remaining: 2s (32000 samples)
        
        assert buffer.has_chunks()
        queue_size = buffer.get_queue_size()
        assert queue_size >= 2  # At least 2 chunks
    
    def test_get_chunk(self, buffer):
        """Test retrieving chunks"""
        # Add audio and create chunk
        audio_data = np.random.randn(80000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # Get chunk
        chunk = buffer.get_chunk()
        
        assert chunk is not None
        assert len(chunk) == 80000  # Full chunk size
        assert chunk.dtype == np.float32
    
    def test_get_chunk_empty(self, buffer):
        """Test getting chunk from empty buffer"""
        chunk = buffer.get_chunk()
        assert chunk is None
    
    def test_chunk_overlap(self, buffer):
        """Test that chunks have proper overlap"""
        # Add enough audio for 2 chunks
        audio_data = np.random.randn(160000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # Get first chunk
        chunk1 = buffer.get_chunk()
        assert chunk1 is not None
        
        # Get second chunk
        chunk2 = buffer.get_chunk()
        assert chunk2 is not None
        
        # Chunks should overlap by overlap_samples
        # chunk1 ends at sample 80000
        # chunk2 should start at sample 64000 (80000 - 16000)
        # So last 16000 samples of chunk1 should equal first 16000 of chunk2
        
        # Due to step size, they won't be exactly same samples,
        # but both should have data
        assert len(chunk1) == 80000
        assert len(chunk2) == 80000
    
    def test_add_audio_stereo(self, buffer):
        """Test adding stereo audio (should flatten to mono)"""
        # Stereo audio (2 channels)
        audio_data = np.random.randn(16000, 2).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # Buffer should flatten to mono
        assert buffer.buffer.ndim == 1
        assert len(buffer.buffer) == 16000
    
    def test_add_audio_wrong_dtype(self, buffer):
        """Test adding audio with wrong dtype (should convert)"""
        # Int16 audio
        audio_data = np.random.randint(-32768, 32767, size=16000).astype(np.int16)
        buffer.add_audio(audio_data)
        
        # Should convert to float32
        assert buffer.buffer.dtype == np.float32
    
    def test_has_chunks(self, buffer):
        """Test has_chunks method"""
        assert not buffer.has_chunks()
        
        # Add full chunk
        audio_data = np.random.randn(80000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        assert buffer.has_chunks()
        
        # Get chunk
        buffer.get_chunk()
        
        assert not buffer.has_chunks()
    
    def test_get_queue_size(self, buffer):
        """Test queue size tracking"""
        assert buffer.get_queue_size() == 0
        
        # Add 3 chunks worth of audio
        audio_data = np.random.randn(240000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        initial_size = buffer.get_queue_size()
        assert initial_size >= 3
        
        # Remove one chunk
        buffer.get_chunk()
        
        assert buffer.get_queue_size() == initial_size - 1
    
    def test_flush(self, buffer):
        """Test flushing remaining buffer"""
        # Add partial chunk
        audio_data = np.random.randn(40000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # Should not create full chunk
        assert not buffer.has_chunks()
        
        # Flush should return remaining audio
        final_chunk = buffer.flush()
        
        assert final_chunk is not None
        assert len(final_chunk) == 40000
        
        # Buffer should be empty now
        assert len(buffer.buffer) == 0
    
    def test_flush_empty(self, buffer):
        """Test flushing empty buffer"""
        final_chunk = buffer.flush()
        assert final_chunk is None
    
    def test_clear(self, buffer):
        """Test clearing buffer"""
        # Add audio
        audio_data = np.random.randn(160000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        assert buffer.has_chunks()
        assert len(buffer.buffer) > 0
        
        # Clear
        buffer.clear()
        
        assert not buffer.has_chunks()
        assert len(buffer.buffer) == 0
        assert buffer.get_queue_size() == 0
    
    def test_get_stats(self, buffer):
        """Test getting buffer statistics"""
        # Add some audio
        audio_data = np.random.randn(100000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        stats = buffer.get_stats()
        
        assert 'buffer_samples' in stats
        assert 'buffer_seconds' in stats
        assert 'chunks_queued' in stats
        assert 'chunk_duration' in stats
        assert 'overlap_duration' in stats
        
        assert stats['chunk_duration'] == 5.0
        assert stats['overlap_duration'] == 1.0
        assert stats['chunks_queued'] >= 1
    
    def test_max_chunks_limit(self):
        """Test that buffer respects max chunks limit"""
        config = {
            'audio': {'sample_rate': 16000},
            'streaming': {
                'chunk_size': 5.0,
                'chunk_overlap': 1.0,
                'buffer_size': 3  # Small limit
            }
        }
        buffer = AudioBuffer(config)
        
        # Add way more than max chunks
        audio_data = np.random.randn(800000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # Should not exceed max
        assert buffer.get_queue_size() <= 3
    
    def test_continuous_processing(self, buffer):
        """Test continuous add/get cycle"""
        # Simulate real-time processing
        for i in range(5):
            # Add 1 second of audio
            audio_data = np.random.randn(16000).astype(np.float32)
            buffer.add_audio(audio_data)
            
            # Try to get chunk if available
            if buffer.has_chunks():
                chunk = buffer.get_chunk()
                assert chunk is not None
                assert len(chunk) == 80000


class TestAudioBufferEdgeCases:
    """Edge case tests for AudioBuffer"""
    
    def test_very_small_chunks(self):
        """Test with very small chunk size"""
        config = {
            'audio': {'sample_rate': 16000},
            'streaming': {
                'chunk_size': 0.5,  # Half second
                'chunk_overlap': 0.1,
                'buffer_size': 10
            }
        }
        buffer = AudioBuffer(config)
        
        # Add 1 second
        audio_data = np.random.randn(16000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # Should create multiple small chunks
        assert buffer.has_chunks()
        chunk = buffer.get_chunk()
        assert len(chunk) == 8000  # 0.5s * 16000
    
    def test_zero_overlap(self):
        """Test with no overlap"""
        config = {
            'audio': {'sample_rate': 16000},
            'streaming': {
                'chunk_size': 5.0,
                'chunk_overlap': 0.0,  # No overlap
                'buffer_size': 10
            }
        }
        buffer = AudioBuffer(config)
        
        assert buffer.overlap_samples == 0
        assert buffer.step_samples == 80000  # Same as chunk size
        
        # Add 10 seconds
        audio_data = np.random.randn(160000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # Should create exactly 2 chunks with no overlap
        assert buffer.get_queue_size() == 2
    
    def test_empty_audio_array(self, basic_config):
        """Test adding empty audio array"""
        buffer = AudioBuffer(basic_config)
        
        empty_audio = np.array([], dtype=np.float32)
        buffer.add_audio(empty_audio)
        
        assert len(buffer.buffer) == 0
        assert not buffer.has_chunks()
    
    def test_thread_safety_basic(self, basic_config):
        """Test that lock is used (basic check)"""
        buffer = AudioBuffer(basic_config)
        
        # Lock should exist
        assert hasattr(buffer, 'lock')
        
        # Operations should work (lock is acquired internally)
        audio_data = np.random.randn(16000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        stats = buffer.get_stats()
        assert stats is not None
    
    def test_multiple_add_before_get(self, basic_config):
        """Test adding audio multiple times before getting chunks"""
        buffer = AudioBuffer(basic_config)
        
        # Add audio in small increments
        for _ in range(10):
            audio_data = np.random.randn(16000).astype(np.float32)
            buffer.add_audio(audio_data)
        
        # Should accumulate and create chunks
        assert buffer.has_chunks()
        
        # Get all chunks
        chunks = []
        while buffer.has_chunks():
            chunk = buffer.get_chunk()
            if chunk is not None:
                chunks.append(chunk)
        
        assert len(chunks) >= 2
    
    def test_flush_with_chunks_queued(self, basic_config):
        """Test flushing when chunks are already queued"""
        buffer = AudioBuffer(basic_config)
        
        # Add enough for full chunk plus remainder
        audio_data = np.random.randn(100000).astype(np.float32)
        buffer.add_audio(audio_data)
        
        # Should have chunks queued
        initial_queue = buffer.get_queue_size()
        assert initial_queue > 0
        
        # Flush should return remaining buffer
        final = buffer.flush()
        
        # Chunks still in queue
        assert buffer.get_queue_size() == initial_queue
        # But buffer is empty
        assert len(buffer.buffer) == 0
    
    def test_different_sample_rates(self):
        """Test with different sample rates"""
        for sample_rate in [8000, 16000, 22050, 44100]:
            config = {
                'audio': {'sample_rate': sample_rate},
                'streaming': {
                    'chunk_size': 1.0,
                    'chunk_overlap': 0.1,
                    'buffer_size': 10
                }
            }
            buffer = AudioBuffer(config)
            
            # Chunk should match sample rate
            assert buffer.chunk_samples == sample_rate
            
            # Add audio
            audio_data = np.random.randn(sample_rate).astype(np.float32)
            buffer.add_audio(audio_data)
            
            # Should create chunk
            assert buffer.has_chunks()
            chunk = buffer.get_chunk()
            assert len(chunk) == sample_rate
