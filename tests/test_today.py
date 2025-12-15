"""
Unit tests for GitHub stats collector (today.py)
Tests the core functionality without making actual API calls
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import sys
import os
from lxml import etree

# Mock environment variables before importing today.py
os.environ['ACCESS_TOKEN'] = 'test_token_mock'
os.environ['USER_NAME'] = 'TestUser'

# Add parent directory to path to import today.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import today


class TestFormatPlural:
    """Tests for format_plural function"""
    
    def test_singular(self):
        assert today.format_plural(1) == ''
    
    def test_plural(self):
        assert today.format_plural(2) == 's'
        assert today.format_plural(0) == 's'
        assert today.format_plural(100) == 's'


class TestStarsCounter:
    """Tests for stars_counter function"""
    
    def test_count_stars(self):
        mock_data = [
            {'node': {'stargazers': {'totalCount': 10}}},
            {'node': {'stargazers': {'totalCount': 25}}},
            {'node': {'stargazers': {'totalCount': 7}}}
        ]
        assert today.stars_counter(mock_data) == 42
    
    def test_count_stars_empty(self):
        assert today.stars_counter([]) == 0


class TestFindAndReplace:
    """Tests for find_and_replace function"""
    
    def test_find_and_replace_existing_element(self):
        svg_content = '''<svg><text id="test_id">old value</text></svg>'''
        root = etree.fromstring(svg_content.encode())
        
        today.find_and_replace(root, 'test_id', 'new value')
        
        element = root.find(".//*[@id='test_id']")
        assert element.text == 'new value'
    
    def test_find_and_replace_nonexistent_element(self):
        svg_content = '''<svg><text id="other_id">value</text></svg>'''
        root = etree.fromstring(svg_content.encode())
        
        # Should not raise an exception
        today.find_and_replace(root, 'nonexistent_id', 'new value')


class TestCommitCounter:
    """Tests for commit_counter function"""
    
    @patch.dict(os.environ, {'USER_NAME': 'TestUser'})
    def test_commit_counter(self):
        mock_file_content = """Comment line 1
Comment line 2
Comment line 3
Comment line 4
Comment line 5
Comment line 6
Comment line 7
abc123hash 100 25 5000 500
def456hash 50 15 3000 300
ghi789hash 75 10 2000 200
"""
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            result = today.commit_counter(7)
            assert result == 50  # 25 + 15 + 10


class TestSVGOverwrite:
    """Tests for svg_overwrite function"""
    
    def test_svg_overwrite_animated(self):
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg">
            <text><tspan id="commit_data">0</tspan></text>
            <text><tspan id="star_data">0</tspan></text>
            <text><tspan id="repo_data">0</tspan></text>
            <text><tspan id="follower_data">0</tspan></text>
            <text><tspan id="loc_data">0</tspan></text>
            <text><tspan id="loc_add">0</tspan></text>
            <text><tspan id="loc_del">0</tspan></text>
        </svg>'''
        
        with patch('builtins.open', mock_open(read_data=svg_content)):
            with patch('lxml.etree.parse') as mock_parse:
                mock_tree = Mock()
                mock_root = etree.fromstring(svg_content.encode())
                mock_tree.getroot.return_value = mock_root
                mock_parse.return_value = mock_tree
                
                today.svg_overwrite('animated.svg', 1234, 567, 89, 12, ['100,000', '120,000', '20,000', True])
                
                # Verify write was called
                mock_tree.write.assert_called_once_with('animated.svg', encoding='utf-8', xml_declaration=False)


class TestGraphReposStars:
    """Tests for graph_repos_stars function"""
    
    @patch.dict(os.environ, {'ACCESS_TOKEN': 'test_token', 'USER_NAME': 'TestUser'})
    @patch('today.simple_request')
    def test_graph_repos_stars_repos(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'repositories': {
                        'totalCount': 42,
                        'edges': []
                    }
                }
            }
        }
        mock_request.return_value = mock_response
        
        result = today.graph_repos_stars('repos', ['OWNER'])
        assert result == 42
    
    @patch.dict(os.environ, {'ACCESS_TOKEN': 'test_token', 'USER_NAME': 'TestUser'})
    @patch('today.simple_request')
    @patch('today.stars_counter')
    def test_graph_repos_stars_stars(self, mock_stars_counter, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_edges = [{'node': {'stargazers': {'totalCount': 10}}}]
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'repositories': {
                        'edges': mock_edges
                    }
                }
            }
        }
        mock_request.return_value = mock_response
        mock_stars_counter.return_value = 100
        
        result = today.graph_repos_stars('stars', ['OWNER'])
        assert result == 100
        mock_stars_counter.assert_called_once_with(mock_edges)


class TestFollowerGetter:
    """Tests for follower_getter function"""
    
    @patch.dict(os.environ, {'ACCESS_TOKEN': 'test_token', 'USER_NAME': 'TestUser'})
    @patch('today.simple_request')
    def test_follower_getter(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'followers': {
                        'totalCount': 196
                    }
                }
            }
        }
        mock_request.return_value = mock_response
        
        result = today.follower_getter('TestUser')
        assert result == 196


class TestUserGetter:
    """Tests for user_getter function"""
    
    @patch.dict(os.environ, {'ACCESS_TOKEN': 'test_token', 'USER_NAME': 'TestUser'})
    @patch('today.simple_request')
    def test_user_getter(self, mock_request):
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'id': 'MDQ6VXNlcjEyMzQ1Njc4',
                    'createdAt': '2020-01-01T00:00:00Z'
                }
            }
        }
        mock_request.return_value = mock_response
        
        user_id, created_at = today.user_getter('TestUser')
        assert user_id == {'id': 'MDQ6VXNlcjEyMzQ1Njc4'}
        assert created_at == '2020-01-01T00:00:00Z'


class TestQueryCount:
    """Tests for query_count function"""
    
    def test_query_count_increments(self):
        today.QUERY_COUNT = {'test_function': 0}
        today.query_count('test_function')
        assert today.QUERY_COUNT['test_function'] == 1
        
        today.query_count('test_function')
        assert today.QUERY_COUNT['test_function'] == 2


class TestPerfCounter:
    """Tests for perf_counter function"""
    
    def test_perf_counter_returns_result_and_time(self):
        def sample_func(x, y):
            return x + y
        
        result, time_taken = today.perf_counter(sample_func, 5, 10)
        
        assert result == 15
        assert isinstance(time_taken, float)
        assert time_taken >= 0


class TestSimpleRequest:
    """Tests for simple_request function"""
    
    @patch.dict(os.environ, {'ACCESS_TOKEN': 'test_token'})
    @patch('requests.post')
    def test_simple_request_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = today.simple_request('test_func', 'query', {'var': 'value'})
        assert result.status_code == 200
    
    @patch.dict(os.environ, {'ACCESS_TOKEN': 'test_token'})
    @patch('requests.post')
    def test_simple_request_failure(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception):
            today.simple_request('test_func', 'query', {'var': 'value'})
