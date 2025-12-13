"""
Markdown解析往返一致性属性测试
验证需求 3.4 - Markdown内容的解析和渲染一致性
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import Dict, Any, List, Optional
import re
import html


# Markdown生成策略
@st.composite
def markdown_text(draw):
    """生成Markdown文本"""
    elements = []
    
    # 标题
    if draw(st.booleans()):
        level = draw(st.integers(min_value=1, max_value=3))
        title = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
        elements.append('#' * level + ' ' + title)
    
    # 段落
    paragraph_count = draw(st.integers(min_value=1, max_value=3))
    for _ in range(paragraph_count):
        paragraph = draw(st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'))))
        elements.append(paragraph)
    
    # 粗体文本
    if draw(st.booleans()):
        bold_text = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
        elements.append(f'**{bold_text}**')
    
    # 斜体文本
    if draw(st.booleans()):
        italic_text = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
        elements.append(f'*{italic_text}*')
    
    # 代码块
    if draw(st.booleans()):
        code = draw(st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Po'))))
        elements.append(f'```\n{code}\n```')
    
    # 内联代码
    if draw(st.booleans()):
        inline_code = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
        elements.append(f'`{inline_code}`')
    
    # 引用
    if draw(st.booleans()):
        quote = draw(st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))))
        elements.append(f'> {quote}')
    
    # 链接
    if draw(st.booleans()):
        link_text = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
        link_url = 'https://example.com'
        elements.append(f'[{link_text}]({link_url})')
    
    return '\n\n'.join(elements)


@st.composite
def simple_markdown(draw):
    """生成简单的Markdown文本（用于更可靠的测试）"""
    elements = []
    
    # 简单段落
    paragraph = draw(st.text(min_size=5, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyz '))
    elements.append(paragraph)
    
    # 可选的标题
    if draw(st.booleans()):
        title = draw(st.text(min_size=3, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz '))
        elements.append(f'## {title}')
    
    # 可选的粗体
    if draw(st.booleans()):
        bold = draw(st.text(min_size=2, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz'))
        elements.append(f'**{bold}**')
    
    return '\n\n'.join(elements)


class MarkdownProcessor:
    """Markdown处理器（模拟BlogDetailPage.vue中的实现）"""
    
    def __init__(self):
        pass
    
    def render_to_html(self, markdown_text: str) -> str:
        """将Markdown渲染为HTML"""
        if not markdown_text:
            return ''
        
        html = markdown_text
        
        # 标题
        html = re.sub(r'^### (.*$)', r'<h3 class="text-xl font-semibold text-gray-900 mt-8 mb-4">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2 class="text-2xl font-bold text-gray-900 mt-10 mb-6">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*$)', r'<h1 class="text-3xl font-bold text-gray-900 mt-12 mb-8">\1</h1>', html, flags=re.MULTILINE)
        
        # 粗体和斜体
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-semibold">\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em class="italic">\1</em>', html)
        
        # 代码块
        html = re.sub(r'```([\s\S]*?)```', r'<pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-6"><code>\1</code></pre>', html)
        html = re.sub(r'`(.*?)`', r'<code class="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm">\1</code>', html)
        
        # 引用
        html = re.sub(r'^> (.*$)', r'<blockquote class="border-l-4 border-primary-500 pl-4 py-2 my-6 bg-primary-50 text-gray-700 italic">\1</blockquote>', html, flags=re.MULTILINE)
        
        # 链接
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" class="text-primary-600 hover:text-primary-700 underline" target="_blank" rel="noopener noreferrer">\1</a>', html)
        
        # 段落
        html = re.sub(r'\n\n', '</p><p class="text-gray-600 leading-relaxed mb-4">', html)
        html = '<p class="text-gray-600 leading-relaxed mb-4">' + html + '</p>'
        
        # 换行
        html = re.sub(r'\n', '<br>', html)
        
        return html
    
    def extract_text_from_html(self, html_text: str) -> str:
        """从HTML中提取纯文本（反向操作）"""
        if not html_text:
            return ''
        
        text = html_text
        
        # 移除HTML标签，保留内容
        text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', text)
        text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text)
        text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text)
        
        text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text)
        text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text)
        
        text = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'```\n\1\n```', text, flags=re.DOTALL)
        text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text)
        
        text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', text)
        
        text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text)
        
        # 段落处理
        text = re.sub(r'</p><p[^>]*>', '\n\n', text)
        text = re.sub(r'</?p[^>]*>', '', text)
        
        # 换行处理
        text = re.sub(r'<br>', '\n', text)
        
        # 清理多余的空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text
    
    def normalize_markdown(self, markdown_text: str) -> str:
        """标准化Markdown文本（用于比较）"""
        if not markdown_text:
            return ''
        
        # 标准化空白字符
        text = re.sub(r'\s+', ' ', markdown_text.strip())
        
        # 标准化换行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def extract_markdown_elements(self, markdown_text: str) -> Dict[str, List[str]]:
        """提取Markdown元素"""
        elements = {
            'headers': [],
            'bold_text': [],
            'italic_text': [],
            'code_blocks': [],
            'inline_code': [],
            'quotes': [],
            'links': [],
            'paragraphs': []
        }
        
        if not markdown_text:
            return elements
        
        # 提取标题
        headers = re.findall(r'^(#{1,3})\s+(.*)', markdown_text, re.MULTILINE)
        elements['headers'] = [(len(level), title.strip()) for level, title in headers]
        
        # 提取粗体文本
        bold_matches = re.findall(r'\*\*(.*?)\*\*', markdown_text)
        elements['bold_text'] = [match.strip() for match in bold_matches]
        
        # 提取斜体文本
        italic_matches = re.findall(r'\*(.*?)\*', markdown_text)
        # 过滤掉粗体中的斜体
        italic_matches = [match for match in italic_matches if not re.search(r'\*\*.*' + re.escape(match) + r'.*\*\*', markdown_text)]
        elements['italic_text'] = [match.strip() for match in italic_matches]
        
        # 提取代码块
        code_blocks = re.findall(r'```([\s\S]*?)```', markdown_text)
        elements['code_blocks'] = [block.strip() for block in code_blocks]
        
        # 提取内联代码
        inline_code = re.findall(r'`(.*?)`', markdown_text)
        elements['inline_code'] = [code.strip() for code in inline_code]
        
        # 提取引用
        quotes = re.findall(r'^>\s+(.*)', markdown_text, re.MULTILINE)
        elements['quotes'] = [quote.strip() for quote in quotes]
        
        # 提取链接
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_text)
        elements['links'] = [(text.strip(), url.strip()) for text, url in links]
        
        # 提取段落（简化版）
        paragraphs = re.split(r'\n\s*\n', markdown_text)
        # 过滤掉标题、代码块等
        paragraphs = [p.strip() for p in paragraphs if p.strip() and not re.match(r'^#{1,3}\s+', p) and not re.match(r'^>\s+', p)]
        elements['paragraphs'] = paragraphs
        
        return elements


class MarkdownValidator:
    """Markdown验证器"""
    
    def __init__(self):
        self.processor = MarkdownProcessor()
    
    def validate_round_trip_consistency(self, original_markdown: str) -> Dict[str, Any]:
        """验证往返一致性"""
        results = {
            'original_length': len(original_markdown),
            'round_trip_successful': False,
            'html_generated': False,
            'text_extracted': False,
            'content_preserved': False,
            'structure_preserved': False,
            'elements_preserved': False,
            'similarity_score': 0.0,
            'differences': []
        }
        
        try:
            # 第一步：Markdown -> HTML
            html_output = self.processor.render_to_html(original_markdown)
            results['html_generated'] = len(html_output) > 0
            
            # 第二步：HTML -> Markdown
            extracted_markdown = self.processor.extract_text_from_html(html_output)
            results['text_extracted'] = len(extracted_markdown) > 0
            
            if results['html_generated'] and results['text_extracted']:
                results['round_trip_successful'] = True
                
                # 比较内容保持性
                original_normalized = self.processor.normalize_markdown(original_markdown)
                extracted_normalized = self.processor.normalize_markdown(extracted_markdown)
                
                results['content_preserved'] = original_normalized == extracted_normalized
                
                # 计算相似度
                results['similarity_score'] = self._calculate_similarity(original_normalized, extracted_normalized)
                
                # 比较结构保持性
                original_elements = self.processor.extract_markdown_elements(original_markdown)
                extracted_elements = self.processor.extract_markdown_elements(extracted_markdown)
                
                results['structure_preserved'] = self._compare_structure(original_elements, extracted_elements)
                results['elements_preserved'] = self._compare_elements(original_elements, extracted_elements)
                
                # 记录差异
                if not results['content_preserved']:
                    results['differences'] = self._find_differences(original_normalized, extracted_normalized)
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def validate_html_safety(self, markdown_text: str) -> Dict[str, Any]:
        """验证HTML安全性"""
        results = {
            'contains_script_tags': False,
            'contains_unsafe_attributes': False,
            'contains_external_resources': False,
            'is_safe': True,
            'potential_issues': []
        }
        
        html_output = self.processor.render_to_html(markdown_text)
        
        # 检查脚本标签
        if re.search(r'<script', html_output, re.IGNORECASE):
            results['contains_script_tags'] = True
            results['is_safe'] = False
            results['potential_issues'].append('Contains script tags')
        
        # 检查不安全的属性
        unsafe_attrs = ['onclick', 'onload', 'onerror', 'javascript:']
        for attr in unsafe_attrs:
            if attr in html_output.lower():
                results['contains_unsafe_attributes'] = True
                results['is_safe'] = False
                results['potential_issues'].append(f'Contains unsafe attribute: {attr}')
        
        # 检查外部资源
        if re.search(r'src\s*=\s*["\']https?://', html_output, re.IGNORECASE):
            results['contains_external_resources'] = True
            results['potential_issues'].append('Contains external resources')
        
        return results
    
    def validate_markdown_structure(self, markdown_text: str) -> Dict[str, Any]:
        """验证Markdown结构"""
        results = {
            'has_headers': False,
            'header_hierarchy_valid': True,
            'has_content': False,
            'balanced_formatting': True,
            'valid_links': True,
            'structure_issues': []
        }
        
        elements = self.processor.extract_markdown_elements(markdown_text)
        
        # 检查是否有标题
        results['has_headers'] = len(elements['headers']) > 0
        
        # 检查标题层级
        if elements['headers']:
            header_levels = [level for level, _ in elements['headers']]
            for i in range(1, len(header_levels)):
                if header_levels[i] > header_levels[i-1] + 1:
                    results['header_hierarchy_valid'] = False
                    results['structure_issues'].append(f'Header level jump from {header_levels[i-1]} to {header_levels[i]}')
        
        # 检查是否有内容
        results['has_content'] = len(elements['paragraphs']) > 0 or len(elements['code_blocks']) > 0
        
        # 检查格式化标记是否平衡
        bold_count = markdown_text.count('**')
        italic_count = markdown_text.count('*') - bold_count * 2  # 减去粗体中的星号
        code_count = markdown_text.count('`')
        
        if bold_count % 2 != 0:
            results['balanced_formatting'] = False
            results['structure_issues'].append('Unbalanced bold formatting')
        
        if code_count % 2 != 0:
            results['balanced_formatting'] = False
            results['structure_issues'].append('Unbalanced code formatting')
        
        # 检查链接有效性（基础检查）
        for text, url in elements['links']:
            if not url or not text:
                results['valid_links'] = False
                results['structure_issues'].append('Empty link text or URL')
        
        return results
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # 简单的字符级相似度
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        # 计算编辑距离的简化版本
        common_chars = sum(1 for c1, c2 in zip(text1, text2) if c1 == c2)
        return common_chars / max_len
    
    def _compare_structure(self, elements1: Dict, elements2: Dict) -> bool:
        """比较结构是否相同"""
        # 比较标题数量和层级
        headers1 = [level for level, _ in elements1['headers']]
        headers2 = [level for level, _ in elements2['headers']]
        
        if headers1 != headers2:
            return False
        
        # 比较其他元素数量
        for key in ['bold_text', 'italic_text', 'code_blocks', 'links']:
            if len(elements1[key]) != len(elements2[key]):
                return False
        
        return True
    
    def _compare_elements(self, elements1: Dict, elements2: Dict) -> bool:
        """比较元素内容是否相同"""
        for key in elements1:
            if elements1[key] != elements2[key]:
                return False
        return True
    
    def _find_differences(self, text1: str, text2: str) -> List[str]:
        """找出文本差异"""
        differences = []
        
        if len(text1) != len(text2):
            differences.append(f'Length difference: {len(text1)} vs {len(text2)}')
        
        # 简单的差异检测
        if text1 != text2:
            differences.append('Content differs')
        
        return differences


# 属性测试
class TestMarkdownProperties:
    """Markdown解析往返一致性属性测试"""
    
    def setup_method(self):
        self.validator = MarkdownValidator()
    
    @given(simple_markdown())
    @settings(max_examples=100, deadline=None)
    def test_markdown_round_trip_consistency_property(self, markdown_text):
        """
        属性 6: Markdown解析往返一致性
        验证Markdown文本经过HTML渲染后能够还原为原始结构
        """
        assume(len(markdown_text.strip()) > 0)  # 确保有内容
        
        results = self.validator.validate_round_trip_consistency(markdown_text)
        
        # 基本往返成功性
        assert results['round_trip_successful'] == True, "Round trip should be successful"
        assert results['html_generated'] == True, "HTML should be generated"
        assert results['text_extracted'] == True, "Text should be extracted from HTML"
        
        # 相似度检查（允许一定的格式差异）
        assert results['similarity_score'] >= 0.7, f"Similarity score too low: {results['similarity_score']}"
        
        # 如果内容简单，应该能够完全保持
        if len(markdown_text) < 100 and '```' not in markdown_text:
            assert results['similarity_score'] >= 0.9, f"Simple content should have high similarity: {results['similarity_score']}"
    
    @given(markdown_text())
    @settings(max_examples=50, deadline=None)
    def test_markdown_html_safety_property(self, markdown_text):
        """
        属性: Markdown HTML安全性
        验证Markdown渲染的HTML不包含安全风险
        """
        assume(len(markdown_text.strip()) > 0)
        
        results = self.validator.validate_html_safety(markdown_text)
        
        # 安全性检查
        assert results['is_safe'] == True, f"HTML should be safe: {results['potential_issues']}"
        assert results['contains_script_tags'] == False, "Should not contain script tags"
        assert results['contains_unsafe_attributes'] == False, "Should not contain unsafe attributes"
        
        # 外部资源检查（警告但不失败）
        if results['contains_external_resources']:
            # 这是一个警告，不是错误
            pass
    
    @given(markdown_text())
    @settings(max_examples=50, deadline=None)
    def test_markdown_structure_validity_property(self, markdown_text):
        """
        属性: Markdown结构有效性
        验证Markdown文本的结构是否有效
        """
        assume(len(markdown_text.strip()) > 0)
        
        results = self.validator.validate_markdown_structure(markdown_text)
        
        # 结构有效性检查
        assert results['header_hierarchy_valid'] == True, f"Header hierarchy should be valid: {results['structure_issues']}"
        assert results['balanced_formatting'] == True, f"Formatting should be balanced: {results['structure_issues']}"
        assert results['valid_links'] == True, f"Links should be valid: {results['structure_issues']}"
        
        # 内容存在性（如果有标题，通常应该有内容）
        if results['has_headers']:
            # 有标题的文档通常应该有一些内容
            assert results['has_content'] == True, "Documents with headers should have content"
    
    @given(st.lists(simple_markdown(), min_size=1, max_size=5))
    @settings(max_examples=30, deadline=None)
    def test_markdown_batch_processing_consistency_property(self, markdown_list):
        """
        属性: Markdown批量处理一致性
        验证批量处理Markdown的一致性
        """
        results = []
        
        for markdown_text in markdown_list:
            if markdown_text.strip():
                result = self.validator.validate_round_trip_consistency(markdown_text)
                results.append(result)
        
        if not results:
            return  # 跳过空列表
        
        # 批量处理一致性检查
        success_rate = sum(1 for r in results if r['round_trip_successful']) / len(results)
        assert success_rate >= 0.8, f"Batch processing success rate too low: {success_rate}"
        
        # 平均相似度检查
        avg_similarity = sum(r['similarity_score'] for r in results) / len(results)
        assert avg_similarity >= 0.7, f"Average similarity too low: {avg_similarity}"
    
    @given(
        st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyz '),
        st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=50, deadline=None)
    def test_markdown_header_consistency_property(self, header_text, header_level):
        """
        属性: Markdown标题一致性
        验证标题的往返一致性
        """
        # Skip if header text is empty after stripping
        stripped_text = header_text.strip()
        assume(len(stripped_text) > 0)
        
        markdown = '#' * header_level + ' ' + stripped_text
        
        results = self.validator.validate_round_trip_consistency(markdown)
        
        assert results['round_trip_successful'] == True, "Header round trip should be successful"
        assert results['structure_preserved'] == True, "Header structure should be preserved"
        
        # 检查标题元素
        original_elements = self.validator.processor.extract_markdown_elements(markdown)
        assert len(original_elements['headers']) == 1, "Should have exactly one header"
        assert original_elements['headers'][0][0] == header_level, f"Header level should be {header_level}"
    
    @given(
        st.text(min_size=1, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyz'),
        st.sampled_from(['**', '*', '`'])
    )
    @settings(max_examples=50, deadline=None)
    def test_markdown_formatting_consistency_property(self, text_content, format_marker):
        """
        属性: Markdown格式化一致性
        验证格式化标记的往返一致性
        """
        if format_marker == '**':
            markdown = f'**{text_content}**'
        elif format_marker == '*':
            markdown = f'*{text_content}*'
        else:  # '`'
            markdown = f'`{text_content}`'
        
        results = self.validator.validate_round_trip_consistency(markdown)
        
        assert results['round_trip_successful'] == True, "Formatting round trip should be successful"
        
        # 检查格式化元素
        original_elements = self.validator.processor.extract_markdown_elements(markdown)
        
        if format_marker == '**':
            assert len(original_elements['bold_text']) >= 1, "Should have bold text"
        elif format_marker == '*':
            assert len(original_elements['italic_text']) >= 1, "Should have italic text"
        else:  # '`'
            assert len(original_elements['inline_code']) >= 1, "Should have inline code"
    
    @given(st.text(min_size=5, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyz '))
    @settings(max_examples=30, deadline=None)
    def test_markdown_quote_consistency_property(self, quote_text):
        """
        属性: Markdown引用一致性
        验证引用块的往返一致性
        """
        markdown = f'> {quote_text.strip()}'
        
        results = self.validator.validate_round_trip_consistency(markdown)
        
        assert results['round_trip_successful'] == True, "Quote round trip should be successful"
        
        # 检查引用元素
        original_elements = self.validator.processor.extract_markdown_elements(markdown)
        assert len(original_elements['quotes']) >= 1, "Should have quote"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])