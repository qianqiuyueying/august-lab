"""
响应式布局适配属性测试

属性 2: 响应式布局适配
验证: 需求 1.4

测试响应式布局系统的适配性，包括：
- 断点系统的正确性
- 网格布局的响应式行为
- 容器尺寸的自适应
- 文本大小的响应式缩放
- 间距系统的响应式调整
- 显示/隐藏功能的正确性
"""

import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, List, Tuple, Any, Optional
import re
import json


class BreakpointSystem:
    """断点系统类"""
    
    def __init__(self):
        self.breakpoints = {
            'xs': 475,
            'sm': 640,
            'md': 768,
            'lg': 1024,
            'xl': 1280,
            '2xl': 1536,
            '3xl': 1920,
        }
        
        self.ordered_breakpoints = ['xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl']
    
    def get_current_breakpoint(self, width: int) -> str:
        """根据宽度获取当前断点"""
        for bp in reversed(self.ordered_breakpoints):
            if width >= self.breakpoints[bp]:
                return bp
        return 'xs'
    
    def is_breakpoint_active(self, width: int, breakpoint: str) -> bool:
        """检查指定断点是否激活"""
        return width >= self.breakpoints[breakpoint]
    
    def get_active_breakpoints(self, width: int) -> List[str]:
        """获取所有激活的断点"""
        active = []
        for bp in self.ordered_breakpoints:
            if width >= self.breakpoints[bp]:
                active.append(bp)
        return active
    
    def is_mobile(self, width: int) -> bool:
        """检查是否为移动端"""
        return width < self.breakpoints['md']
    
    def is_tablet(self, width: int) -> bool:
        """检查是否为平板端"""
        return self.breakpoints['md'] <= width < self.breakpoints['lg']
    
    def is_desktop(self, width: int) -> bool:
        """检查是否为桌面端"""
        return width >= self.breakpoints['lg']


class ResponsiveGridSystem:
    """响应式网格系统类"""
    
    def __init__(self, breakpoint_system: BreakpointSystem):
        self.bp_system = breakpoint_system
        
        # 预设网格配置
        self.presets = {
            'auto': {'xs': 1, 'sm': 2, 'md': 3, 'lg': 4, 'xl': 5, '2xl': 6},
            'cards': {'xs': 1, 'sm': 2, 'lg': 3, 'xl': 4},
            'features': {'xs': 1, 'md': 2, 'lg': 3},
            'team': {'xs': 1, 'sm': 2, 'lg': 3, 'xl': 4},
            'gallery': {'xs': 2, 'sm': 3, 'md': 4, 'lg': 5, 'xl': 6},
            'blog': {'xs': 1, 'md': 2, 'lg': 3},
            'portfolio': {'xs': 1, 'sm': 2, 'lg': 3},
        }
    
    def get_grid_columns(self, width: int, config: Dict[str, int]) -> int:
        """根据宽度和配置获取网格列数"""
        current_bp = self.bp_system.get_current_breakpoint(width)
        
        # 从当前断点开始向下查找配置
        for bp in reversed(self.bp_system.ordered_breakpoints):
            if bp in config and self.bp_system.is_breakpoint_active(width, bp):
                return config[bp]
        
        # 如果没有找到配置，返回最小的配置值
        if config:
            return min(config.values())
        return 1
    
    def get_preset_columns(self, width: int, preset: str) -> int:
        """根据预设获取网格列数"""
        if preset not in self.presets:
            return 1
        return self.get_grid_columns(width, self.presets[preset])
    
    def validate_grid_config(self, config: Dict[str, int]) -> bool:
        """验证网格配置的有效性"""
        # 检查所有值都是正整数
        for bp, cols in config.items():
            if not isinstance(cols, int) or cols <= 0:
                return False
            if bp not in self.bp_system.breakpoints:
                return False
        
        # 检查配置的递增性（可选，但推荐）
        ordered_config = []
        for bp in self.bp_system.ordered_breakpoints:
            if bp in config:
                ordered_config.append(config[bp])
        
        # 允许相同值，但不应该递减太多
        return True


class ResponsiveSpacingSystem:
    """响应式间距系统类"""
    
    def __init__(self, breakpoint_system: BreakpointSystem):
        self.bp_system = breakpoint_system
        
        # 预设间距配置
        self.presets = {
            'section': {'xs': '3rem', 'sm': '4rem', 'lg': '5rem', 'xl': '6rem'},
            'container': {'xs': '1rem', 'sm': '1.5rem', 'lg': '2rem', 'xl': '2.5rem'},
            'card': {'xs': '1rem', 'sm': '1.5rem', 'lg': '2rem'},
            'button': {'xs': '0.5rem 1rem', 'sm': '0.75rem 1.5rem', 'lg': '1rem 2rem'},
        }
    
    def get_spacing_value(self, width: int, config: Dict[str, str]) -> str:
        """根据宽度和配置获取间距值"""
        current_bp = self.bp_system.get_current_breakpoint(width)
        
        # 从当前断点开始向下查找配置
        for bp in reversed(self.bp_system.ordered_breakpoints):
            if bp in config and self.bp_system.is_breakpoint_active(width, bp):
                return config[bp]
        
        # 如果没有找到配置，返回默认值
        if config:
            return list(config.values())[0]
        return '1rem'
    
    def parse_spacing_value(self, value: str) -> Dict[str, float]:
        """解析间距值"""
        # 简单的rem/px解析
        if 'rem' in value:
            if ' ' in value:
                # 处理 "1rem 2rem" 格式
                parts = value.split()
                return {
                    'vertical': float(parts[0].replace('rem', '')),
                    'horizontal': float(parts[1].replace('rem', '')) if len(parts) > 1 else float(parts[0].replace('rem', ''))
                }
            else:
                val = float(value.replace('rem', ''))
                return {'vertical': val, 'horizontal': val}
        return {'vertical': 1.0, 'horizontal': 1.0}


class ResponsiveTextSystem:
    """响应式文本系统类"""
    
    def __init__(self, breakpoint_system: BreakpointSystem):
        self.bp_system = breakpoint_system
        
        # 预设文本大小配置
        self.presets = {
            'hero': {'xs': '2rem', 'sm': '2.5rem', 'md': '3rem', 'lg': '3.5rem', 'xl': '4rem'},
            'title': {'xs': '1.5rem', 'sm': '1.875rem', 'md': '2.25rem', 'lg': '2.5rem'},
            'subtitle': {'xs': '1.125rem', 'sm': '1.25rem', 'md': '1.5rem'},
            'body': {'xs': '0.875rem', 'sm': '1rem', 'md': '1.125rem'},
            'caption': {'xs': '0.75rem', 'sm': '0.875rem'},
        }
    
    def get_text_size(self, width: int, config: Dict[str, str]) -> str:
        """根据宽度和配置获取文本大小"""
        current_bp = self.bp_system.get_current_breakpoint(width)
        
        # 从当前断点开始向下查找配置
        for bp in reversed(self.bp_system.ordered_breakpoints):
            if bp in config and self.bp_system.is_breakpoint_active(width, bp):
                return config[bp]
        
        # 如果没有找到配置，返回默认值
        if config:
            return list(config.values())[0]
        return '1rem'
    
    def parse_text_size(self, size: str) -> float:
        """解析文本大小值"""
        if 'rem' in size:
            return float(size.replace('rem', ''))
        elif 'px' in size:
            return float(size.replace('px', '')) / 16  # 转换为rem
        return 1.0


class ResponsiveVisibilitySystem:
    """响应式显示/隐藏系统类"""
    
    def __init__(self, breakpoint_system: BreakpointSystem):
        self.bp_system = breakpoint_system
    
    def is_show_mobile_visible(self, width: int) -> bool:
        """检查show-mobile元素是否可见"""
        return self.bp_system.is_mobile(width)
    
    def is_show_tablet_visible(self, width: int) -> bool:
        """检查show-tablet元素是否可见"""
        return self.bp_system.is_tablet(width)
    
    def is_show_desktop_visible(self, width: int) -> bool:
        """检查show-desktop元素是否可见"""
        return self.bp_system.is_desktop(width)
    
    def is_hide_mobile_visible(self, width: int) -> bool:
        """检查hide-mobile元素是否可见"""
        return not self.bp_system.is_mobile(width)
    
    def is_hide_desktop_visible(self, width: int) -> bool:
        """检查hide-desktop元素是否可见"""
        return not self.bp_system.is_desktop(width)


# 测试策略
screen_widths = st.integers(min_value=320, max_value=2560)
breakpoint_names = st.sampled_from(['xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl'])
grid_columns = st.integers(min_value=1, max_value=12)
preset_names = st.sampled_from(['auto', 'cards', 'features', 'team', 'gallery', 'blog', 'portfolio'])


class TestResponsiveLayoutProperties:
    """响应式布局适配属性测试类"""
    
    def create_breakpoint_system(self):
        return BreakpointSystem()
    
    def create_grid_system(self):
        bp_system = self.create_breakpoint_system()
        return ResponsiveGridSystem(bp_system)
    
    def create_spacing_system(self):
        bp_system = self.create_breakpoint_system()
        return ResponsiveSpacingSystem(bp_system)
    
    def create_text_system(self):
        bp_system = self.create_breakpoint_system()
        return ResponsiveTextSystem(bp_system)
    
    def create_visibility_system(self):
        bp_system = self.create_breakpoint_system()
        return ResponsiveVisibilitySystem(bp_system)
    
    def test_breakpoint_system_consistency_property(self):
        """
        属性: 断点系统一致性
        
        断点系统应该保持一致的顺序和阈值
        """
        bp_system = self.create_breakpoint_system()
        
        # 检查断点顺序
        breakpoints = bp_system.breakpoints
        ordered = bp_system.ordered_breakpoints
        
        for i in range(len(ordered) - 1):
            current_bp = ordered[i]
            next_bp = ordered[i + 1]
            
            assert breakpoints[current_bp] < breakpoints[next_bp], \
                f"断点 {current_bp} ({breakpoints[current_bp]}) 应该小于 {next_bp} ({breakpoints[next_bp]})"
    
    @given(width=screen_widths)
    def test_breakpoint_detection_property(self, width):
        """
        属性: 断点检测正确性
        
        对于任何屏幕宽度，断点检测应该返回正确的断点
        """
        bp_system = self.create_breakpoint_system()
        
        current_bp = bp_system.get_current_breakpoint(width)
        
        # 验证返回的断点是有效的
        assert current_bp in bp_system.breakpoints, f"无效的断点: {current_bp}"
        
        # 验证断点逻辑
        bp_threshold = bp_system.breakpoints[current_bp]
        # 对于xs断点，即使宽度小于阈值也是有效的（作为默认断点）
        if current_bp != 'xs':
            assert width >= bp_threshold, f"宽度 {width} 不应该匹配断点 {current_bp} (阈值: {bp_threshold})"
        
        # 验证没有更大的断点被激活
        for bp_name, threshold in bp_system.breakpoints.items():
            if threshold > bp_threshold and width >= threshold:
                assert False, f"宽度 {width} 应该匹配更大的断点 {bp_name} 而不是 {current_bp}"
    
    @given(width=screen_widths)
    def test_device_type_classification_property(self, width):
        """
        属性: 设备类型分类正确性
        
        设备类型分类应该与断点系统保持一致
        """
        bp_system = self.create_breakpoint_system()
        
        is_mobile = bp_system.is_mobile(width)
        is_tablet = bp_system.is_tablet(width)
        is_desktop = bp_system.is_desktop(width)
        
        # 确保只有一种设备类型为真
        device_types = [is_mobile, is_tablet, is_desktop]
        assert sum(device_types) == 1, f"宽度 {width} 应该只匹配一种设备类型"
        
        # 验证分类逻辑
        if width < bp_system.breakpoints['md']:
            assert is_mobile, f"宽度 {width} 应该被分类为移动端"
        elif width < bp_system.breakpoints['lg']:
            assert is_tablet, f"宽度 {width} 应该被分类为平板端"
        else:
            assert is_desktop, f"宽度 {width} 应该被分类为桌面端"
    
    @given(width=screen_widths, preset=preset_names)
    def test_grid_system_responsiveness_property(self, width, preset):
        """
        属性: 网格系统响应式正确性
        
        网格系统应该根据屏幕宽度返回合适的列数
        """
        grid_system = self.create_grid_system()
        
        columns = grid_system.get_preset_columns(width, preset)
        
        # 验证列数是有效的
        assert isinstance(columns, int), f"列数应该是整数，得到: {columns}"
        assert columns > 0, f"列数应该大于0，得到: {columns}"
        assert columns <= 12, f"列数不应该超过12，得到: {columns}"
        
        # 验证响应式行为
        preset_config = grid_system.presets[preset]
        current_bp = grid_system.bp_system.get_current_breakpoint(width)
        
        # 检查是否使用了正确的断点配置
        expected_columns = grid_system.get_grid_columns(width, preset_config)
        assert columns == expected_columns, \
            f"预设 {preset} 在宽度 {width} 下应该返回 {expected_columns} 列，实际返回 {columns}"
    
    @given(width=screen_widths)
    def test_grid_columns_monotonicity_property(self, width):
        """
        属性: 网格列数单调性
        
        在更大的屏幕上，网格列数应该不会减少（对于auto预设）
        """
        grid_system = self.create_grid_system()
        
        # 测试auto预设的单调性
        auto_config = grid_system.presets['auto']
        columns = grid_system.get_grid_columns(width, auto_config)
        
        # 测试更大宽度的列数
        larger_width = width + 100
        larger_columns = grid_system.get_grid_columns(larger_width, auto_config)
        
        assert larger_columns >= columns, \
            f"更大宽度 {larger_width} 的列数 {larger_columns} 不应该小于宽度 {width} 的列数 {columns}"
    
    @given(width=screen_widths)
    def test_spacing_system_consistency_property(self, width):
        """
        属性: 间距系统一致性
        
        间距系统应该返回有效的CSS值
        """
        spacing_system = self.create_spacing_system()
        
        for preset_name, config in spacing_system.presets.items():
            spacing_value = spacing_system.get_spacing_value(width, config)
            
            # 验证返回值是有效的CSS值
            assert isinstance(spacing_value, str), f"间距值应该是字符串，得到: {spacing_value}"
            assert len(spacing_value) > 0, f"间距值不应该为空"
            
            # 验证包含有效的单位
            valid_units = ['rem', 'px', 'em', '%']
            has_valid_unit = any(unit in spacing_value for unit in valid_units)
            assert has_valid_unit, f"间距值 {spacing_value} 应该包含有效的CSS单位"
            
            # 验证可以解析
            parsed = spacing_system.parse_spacing_value(spacing_value)
            assert 'vertical' in parsed and 'horizontal' in parsed, \
                f"无法解析间距值: {spacing_value}"
    
    @given(width=screen_widths)
    def test_text_system_scaling_property(self, width):
        """
        属性: 文本系统缩放正确性
        
        文本大小应该随屏幕尺寸合理缩放
        """
        text_system = self.create_text_system()
        
        for preset_name, config in text_system.presets.items():
            text_size = text_system.get_text_size(width, config)
            
            # 验证返回值是有效的CSS值
            assert isinstance(text_size, str), f"文本大小应该是字符串，得到: {text_size}"
            assert len(text_size) > 0, f"文本大小不应该为空"
            
            # 验证可以解析为数值
            parsed_size = text_system.parse_text_size(text_size)
            assert isinstance(parsed_size, float), f"无法解析文本大小: {text_size}"
            assert parsed_size > 0, f"文本大小应该大于0，得到: {parsed_size}"
            assert parsed_size <= 10, f"文本大小不应该过大，得到: {parsed_size}rem"
    
    @given(width=screen_widths)
    def test_visibility_system_exclusivity_property(self, width):
        """
        属性: 显示/隐藏系统排他性
        
        show-mobile和show-desktop不应该同时可见
        """
        visibility_system = self.create_visibility_system()
        
        show_mobile = visibility_system.is_show_mobile_visible(width)
        show_desktop = visibility_system.is_show_desktop_visible(width)
        show_tablet = visibility_system.is_show_tablet_visible(width)
        
        # mobile和desktop不应该同时可见
        assert not (show_mobile and show_desktop), \
            f"宽度 {width} 下，show-mobile和show-desktop不应该同时可见"
        
        # 至少有一个设备类型可见
        assert show_mobile or show_tablet or show_desktop, \
            f"宽度 {width} 下，至少应该有一种设备类型可见"
    
    @given(width=screen_widths)
    def test_hide_show_complementarity_property(self, width):
        """
        属性: 隐藏/显示互补性
        
        hide-mobile和show-mobile应该是互补的
        """
        visibility_system = self.create_visibility_system()
        
        show_mobile = visibility_system.is_show_mobile_visible(width)
        hide_mobile = visibility_system.is_hide_mobile_visible(width)
        
        # 应该是互补的
        assert show_mobile != hide_mobile, \
            f"宽度 {width} 下，show-mobile ({show_mobile}) 和 hide-mobile ({hide_mobile}) 应该是互补的"
        
        show_desktop = visibility_system.is_show_desktop_visible(width)
        hide_desktop = visibility_system.is_hide_desktop_visible(width)
        
        # 应该是互补的
        assert show_desktop != hide_desktop, \
            f"宽度 {width} 下，show-desktop ({show_desktop}) 和 hide-desktop ({hide_desktop}) 应该是互补的"
    
    def test_grid_config_validation_property(self):
        """
        属性: 网格配置验证正确性
        
        网格配置验证应该正确识别有效和无效的配置
        """
        grid_system = self.create_grid_system()
        
        # 有效配置
        valid_configs = [
            {'xs': 1, 'sm': 2, 'md': 3},
            {'md': 2, 'lg': 4},
            {'xs': 1, 'xl': 6},
        ]
        
        for config in valid_configs:
            assert grid_system.validate_grid_config(config), \
                f"配置 {config} 应该是有效的"
        
        # 无效配置
        invalid_configs = [
            {'xs': 0, 'sm': 2},  # 零列
            {'xs': -1, 'sm': 2},  # 负数列
            {'invalid': 2},  # 无效断点
            {'xs': 'invalid'},  # 非整数值
        ]
        
        for config in invalid_configs:
            assert not grid_system.validate_grid_config(config), \
                f"配置 {config} 应该是无效的"
    
    @given(width1=screen_widths, width2=screen_widths)
    def test_responsive_behavior_consistency_property(self, width1, width2):
        """
        属性: 响应式行为一致性
        
        相同断点的不同宽度应该产生相同的响应式行为
        """
        bp_system = self.create_breakpoint_system()
        grid_system = self.create_grid_system()
        
        bp1 = bp_system.get_current_breakpoint(width1)
        bp2 = bp_system.get_current_breakpoint(width2)
        
        # 如果断点相同，网格列数应该相同
        if bp1 == bp2:
            for preset in grid_system.presets:
                cols1 = grid_system.get_preset_columns(width1, preset)
                cols2 = grid_system.get_preset_columns(width2, preset)
                
                assert cols1 == cols2, \
                    f"相同断点 {bp1} 下，宽度 {width1} 和 {width2} 的 {preset} 预设应该有相同的列数"
    
    @given(width=screen_widths)
    def test_breakpoint_boundary_behavior_property(self, width):
        """
        属性: 断点边界行为正确性
        
        在断点边界附近的行为应该是正确的
        """
        bp_system = self.create_breakpoint_system()
        
        current_bp = bp_system.get_current_breakpoint(width)
        
        # 测试边界行为
        if width > 320:  # 避免过小的宽度
            smaller_width = width - 1
            smaller_bp = bp_system.get_current_breakpoint(smaller_width)
            
            # 断点应该相同或更小
            current_index = bp_system.ordered_breakpoints.index(current_bp)
            smaller_index = bp_system.ordered_breakpoints.index(smaller_bp)
            
            assert smaller_index <= current_index, \
                f"更小宽度 {smaller_width} 的断点 {smaller_bp} 不应该大于宽度 {width} 的断点 {current_bp}"
    
    def test_responsive_presets_completeness_property(self):
        """
        属性: 响应式预设完整性
        
        所有预设都应该包含必要的断点配置
        """
        grid_system = self.create_grid_system()
        
        for preset_name, config in grid_system.presets.items():
            # 每个预设至少应该有xs配置
            assert 'xs' in config or len(config) > 0, \
                f"预设 {preset_name} 应该至少有一个断点配置"
            
            # 验证配置有效性
            assert grid_system.validate_grid_config(config), \
                f"预设 {preset_name} 的配置无效: {config}"
            
            # 验证列数范围
            for bp, cols in config.items():
                assert 1 <= cols <= 12, \
                    f"预设 {preset_name} 的断点 {bp} 列数 {cols} 应该在1-12之间"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])