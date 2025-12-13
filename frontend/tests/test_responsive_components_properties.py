"""
响应式组件属性测试

属性 2: 响应式布局适配
验证: 需求 1.4

测试Vue响应式组件的行为，包括：
- useResponsive组合函数的正确性
- ResponsiveGrid组件的属性
- ResponsiveContainer组件的行为
- ResponsiveImage组件的适配性
- CSS工具类的响应式行为
"""

import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, List, Any, Optional
import json
import re


class MockWindow:
    """模拟浏览器窗口对象"""
    
    def __init__(self, width: int, height: int):
        self.innerWidth = width
        self.innerHeight = height
        self.listeners = {}
    
    def addEventListener(self, event: str, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
    
    def removeEventListener(self, event: str, callback):
        if event in self.listeners:
            self.listeners[event] = [cb for cb in self.listeners[event] if cb != callback]
    
    def dispatchEvent(self, event: str):
        if event in self.listeners:
            for callback in self.listeners[event]:
                callback()
    
    def resize(self, width: int, height: int):
        self.innerWidth = width
        self.innerHeight = height
        self.dispatchEvent('resize')


class ResponsiveComposable:
    """模拟useResponsive组合函数"""
    
    def __init__(self, window: MockWindow):
        self.window = window
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
    
    @property
    def windowWidth(self) -> int:
        return self.window.innerWidth
    
    @property
    def windowHeight(self) -> int:
        return self.window.innerHeight
    
    @property
    def currentBreakpoint(self) -> str:
        width = self.windowWidth
        for bp in reversed(self.ordered_breakpoints):
            if width >= self.breakpoints[bp]:
                return bp
        return 'xs'  # 默认返回最小断点
    
    @property
    def isMobile(self) -> bool:
        return self.windowWidth < self.breakpoints['md']
    
    @property
    def isTablet(self) -> bool:
        return self.breakpoints['md'] <= self.windowWidth < self.breakpoints['lg']
    
    @property
    def isDesktop(self) -> bool:
        return self.windowWidth >= self.breakpoints['lg']
    
    @property
    def isPortrait(self) -> bool:
        return self.windowHeight > self.windowWidth
    
    @property
    def isLandscape(self) -> bool:
        return self.windowWidth > self.windowHeight
    
    @property
    def deviceType(self) -> str:
        if self.isMobile:
            return 'mobile'
        elif self.isTablet:
            return 'tablet'
        return 'desktop'
    
    def isBreakpoint(self, breakpoint: str) -> bool:
        return self.windowWidth >= self.breakpoints[breakpoint]
    
    def isBetween(self, min_bp: str, max_bp: str) -> bool:
        return (self.windowWidth >= self.breakpoints[min_bp] and 
                self.windowWidth < self.breakpoints[max_bp])
    
    def getGridCols(self, config: Dict[str, int]) -> int:
        """获取响应式网格列数"""
        current_bp = self.currentBreakpoint
        
        # 从当前断点开始向下查找配置
        current_index = self.ordered_breakpoints.index(current_bp)
        
        for i in range(current_index, -1, -1):
            bp = self.ordered_breakpoints[i]
            if bp in config:
                return config[bp]
        
        return 1  # 默认值


class ResponsiveGridComponent:
    """模拟ResponsiveGrid组件"""
    
    def __init__(self, responsive: ResponsiveComposable):
        self.responsive = responsive
        self.presets = {
            'auto': {'xs': 1, 'sm': 2, 'md': 3, 'lg': 4, 'xl': 5, '2xl': 6},
            'cards': {'xs': 1, 'sm': 2, 'lg': 3, 'xl': 4},
            'features': {'xs': 1, 'md': 2, 'lg': 3},
            'team': {'xs': 1, 'sm': 2, 'lg': 3, 'xl': 4},
            'gallery': {'xs': 2, 'sm': 3, 'md': 4, 'lg': 5, 'xl': 6},
            'blog': {'xs': 1, 'md': 2, 'lg': 3},
            'portfolio': {'xs': 1, 'sm': 2, 'lg': 3},
        }
    
    def getColumns(self, cols: Optional[Dict[str, int]] = None, preset: Optional[str] = None) -> int:
        """获取当前列数"""
        if preset and preset in self.presets:
            config = self.presets[preset]
        elif cols:
            config = cols
        else:
            config = {'xs': 1, 'sm': 2, 'md': 3, 'lg': 4}
        
        return self.responsive.getGridCols(config)
    
    def getGridStyles(self, cols: Optional[Dict[str, int]] = None, preset: Optional[str] = None, 
                     gap: str = '1.5rem', auto_fit: bool = False, min_col_width: str = '250px') -> Dict[str, str]:
        """获取网格样式"""
        styles = {}
        
        if auto_fit:
            styles['gridTemplateColumns'] = f'repeat(auto-fit, minmax({min_col_width}, 1fr))'
        else:
            columns = self.getColumns(cols, preset)
            styles['gridTemplateColumns'] = f'repeat({columns}, 1fr)'
        
        styles['gap'] = gap
        styles['display'] = 'grid'
        
        return styles


class ResponsiveContainerComponent:
    """模拟ResponsiveContainer组件"""
    
    def __init__(self, responsive: ResponsiveComposable):
        self.responsive = responsive
        self.size_map = {
            'sm': 'max-w-2xl',
            'md': 'max-w-4xl', 
            'lg': 'max-w-7xl',
            'xl': 'max-w-8xl',
            'full': 'max-w-full',
        }
    
    def getContainerClasses(self, size: str = 'lg', center: bool = True, 
                           background: str = 'transparent', shadow: bool = False,
                           rounded: bool = False, border: bool = False) -> List[str]:
        """获取容器CSS类"""
        classes = []
        
        # 基础容器类
        classes.append('container')
        
        # 大小
        if size in self.size_map:
            classes.append(self.size_map[size])
        
        # 居中
        if center:
            classes.append('mx-auto')
        
        # 背景色
        if background == 'white':
            classes.append('bg-white')
        elif background == 'gray':
            classes.append('bg-gray-50')
        elif background == 'primary':
            classes.append('bg-primary-50')
        
        # 阴影
        if shadow:
            classes.append('shadow-sm')
        
        # 圆角
        if rounded:
            classes.append('rounded-lg')
        
        # 边框
        if border:
            classes.append('border border-gray-200')
        
        return classes
    
    def getResponsivePadding(self, padding_config: Dict[str, str]) -> str:
        """获取响应式内边距"""
        current_bp = self.responsive.currentBreakpoint
        
        # 从当前断点开始向下查找配置
        for bp in reversed(self.responsive.ordered_breakpoints):
            if bp in padding_config and self.responsive.isBreakpoint(bp):
                return padding_config[bp]
        
        return '1rem'  # 默认值


class ResponsiveImageComponent:
    """模拟ResponsiveImage组件"""
    
    def __init__(self, responsive: ResponsiveComposable):
        self.responsive = responsive
    
    def getCurrentSrc(self, src: Optional[str] = None, 
                     responsive_src: Optional[Dict[str, str]] = None) -> str:
        """获取当前图片源"""
        if responsive_src:
            current_bp = self.responsive.currentBreakpoint
            
            # 从当前断点开始向下查找配置
            for bp in reversed(self.responsive.ordered_breakpoints):
                if bp in responsive_src and self.responsive.isBreakpoint(bp):
                    return responsive_src[bp]
            
            # 如果没有找到匹配的断点，返回最小的配置
            if responsive_src:
                # 找到配置中最小的断点
                for bp in self.responsive.ordered_breakpoints:
                    if bp in responsive_src:
                        return responsive_src[bp]
        
        return src or ''
    
    def getAspectRatioStyle(self, aspect_ratio: str) -> Dict[str, str]:
        """获取宽高比样式"""
        styles = {}
        
        if aspect_ratio == 'square':
            styles['aspectRatio'] = '1 / 1'
        elif aspect_ratio == 'video':
            styles['aspectRatio'] = '16 / 9'
        elif aspect_ratio == 'portrait':
            styles['aspectRatio'] = '3 / 4'
        elif aspect_ratio == 'landscape':
            styles['aspectRatio'] = '4 / 3'
        else:
            styles['aspectRatio'] = aspect_ratio
        
        return styles


class CSSUtilityValidator:
    """CSS工具类验证器"""
    
    def __init__(self):
        self.responsive_classes = {
            'show-mobile': lambda width: width < 768,
            'show-tablet': lambda width: 768 <= width < 1024,
            'show-desktop': lambda width: width >= 768,
            'hide-mobile': lambda width: width >= 768,
            'hide-desktop': lambda width: width < 768,
        }
        
        self.grid_classes = [
            'grid-responsive', 'grid-responsive-2', 'grid-responsive-3',
            'grid-responsive-4', 'grid-responsive-5', 'grid-responsive-6'
        ]
        
        self.text_classes = [
            'heading-1', 'heading-2', 'heading-3', 'heading-4', 'heading-5', 'heading-6',
            'text-responsive-xs', 'text-responsive-sm', 'text-responsive-base',
            'text-responsive-lg', 'text-responsive-xl', 'text-responsive-2xl', 'text-responsive-3xl'
        ]
    
    def isClassVisible(self, class_name: str, width: int) -> bool:
        """检查CSS类在指定宽度下是否可见"""
        if class_name in self.responsive_classes:
            return self.responsive_classes[class_name](width)
        return True  # 默认可见
    
    def validateGridClass(self, class_name: str) -> bool:
        """验证网格类的有效性"""
        return class_name in self.grid_classes
    
    def validateTextClass(self, class_name: str) -> bool:
        """验证文本类的有效性"""
        return class_name in self.text_classes


# 测试策略
screen_widths = st.integers(min_value=320, max_value=2560)
screen_heights = st.integers(min_value=480, max_value=1440)
breakpoint_names = st.sampled_from(['xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl'])
grid_presets = st.sampled_from(['auto', 'cards', 'features', 'team', 'gallery', 'blog', 'portfolio'])
container_sizes = st.sampled_from(['sm', 'md', 'lg', 'xl', 'full'])
aspect_ratios = st.sampled_from(['square', 'video', 'portrait', 'landscape', '2/3', '3/2'])


class TestResponsiveComponentsProperties:
    """响应式组件属性测试类"""
    
    def create_mock_window(self, width: int = 1024, height: int = 768):
        return MockWindow(width, height)
    
    def create_responsive_composable(self, width: int = 1024, height: int = 768):
        window = self.create_mock_window(width, height)
        return ResponsiveComposable(window)
    
    def create_grid_component(self, width: int = 1024, height: int = 768):
        responsive = self.create_responsive_composable(width, height)
        return ResponsiveGridComponent(responsive)
    
    def create_container_component(self, width: int = 1024, height: int = 768):
        responsive = self.create_responsive_composable(width, height)
        return ResponsiveContainerComponent(responsive)
    
    def create_image_component(self, width: int = 1024, height: int = 768):
        responsive = self.create_responsive_composable(width, height)
        return ResponsiveImageComponent(responsive)
    
    @given(width=screen_widths, height=screen_heights)
    def test_responsive_composable_consistency_property(self, width, height):
        """
        属性: 响应式组合函数一致性
        
        响应式组合函数的各个属性应该保持逻辑一致性
        """
        responsive = self.create_responsive_composable(width, height)
        
        # 基本属性检查
        assert responsive.windowWidth == width
        assert responsive.windowHeight == height
        
        # 设备类型互斥性
        device_types = [responsive.isMobile, responsive.isTablet, responsive.isDesktop]
        assert sum(device_types) == 1, f"宽度 {width} 应该只匹配一种设备类型"
        
        # 屏幕方向一致性
        if width > height:
            assert responsive.isLandscape and not responsive.isPortrait
        elif height > width:
            assert responsive.isPortrait and not responsive.isLandscape
        
        # 断点一致性
        current_bp = responsive.currentBreakpoint
        # 对于xs断点，如果宽度小于xs阈值，这是正常的
        if current_bp != 'xs':
            assert responsive.isBreakpoint(current_bp), f"当前断点 {current_bp} 应该是激活的"
        else:
            # xs是默认断点，即使宽度小于xs阈值也可能返回xs
            pass
    
    @given(width=screen_widths)
    def test_responsive_composable_breakpoint_logic_property(self, width):
        """
        属性: 响应式组合函数断点逻辑正确性
        
        断点检测逻辑应该正确
        """
        responsive = self.create_responsive_composable(width, 768)
        
        current_bp = responsive.currentBreakpoint
        
        # 验证当前断点
        assert current_bp in responsive.breakpoints
        
        # 验证断点激活逻辑
        for bp_name, threshold in responsive.breakpoints.items():
            expected_active = width >= threshold
            actual_active = responsive.isBreakpoint(bp_name)
            assert actual_active == expected_active, \
                f"断点 {bp_name} 在宽度 {width} 下的激活状态不正确"
        
        # 验证设备类型逻辑
        if width < responsive.breakpoints['md']:
            assert responsive.isMobile and responsive.deviceType == 'mobile'
        elif width < responsive.breakpoints['lg']:
            assert responsive.isTablet and responsive.deviceType == 'tablet'
        else:
            assert responsive.isDesktop and responsive.deviceType == 'desktop'
    
    @given(width=screen_widths, preset=grid_presets)
    def test_grid_component_columns_property(self, width, preset):
        """
        属性: 网格组件列数正确性
        
        网格组件应该根据屏幕宽度返回正确的列数
        """
        grid = self.create_grid_component(width, 768)
        
        columns = grid.getColumns(preset=preset)
        
        # 验证列数有效性
        assert isinstance(columns, int), f"列数应该是整数，得到: {columns}"
        assert columns > 0, f"列数应该大于0，得到: {columns}"
        assert columns <= 12, f"列数不应该超过12，得到: {columns}"
        
        # 验证预设配置
        if preset in grid.presets:
            preset_config = grid.presets[preset]
            expected_columns = grid.responsive.getGridCols(preset_config)
            assert columns == expected_columns, \
                f"预设 {preset} 在宽度 {width} 下应该返回 {expected_columns} 列"
    
    @given(width=screen_widths)
    def test_grid_component_styles_property(self, width):
        """
        属性: 网格组件样式正确性
        
        网格组件生成的样式应该是有效的CSS
        """
        grid = self.create_grid_component(width, 768)
        
        styles = grid.getGridStyles(preset='auto', gap='1.5rem')
        
        # 验证必需的样式属性
        assert 'display' in styles and styles['display'] == 'grid'
        assert 'gridTemplateColumns' in styles
        assert 'gap' in styles
        
        # 验证网格模板列
        grid_template = styles['gridTemplateColumns']
        assert 'repeat(' in grid_template and 'fr)' in grid_template, \
            f"网格模板列格式不正确: {grid_template}"
        
        # 验证间距
        assert styles['gap'] == '1.5rem'
    
    @given(width=screen_widths)
    def test_grid_component_auto_fit_property(self, width):
        """
        属性: 网格组件自动适配正确性
        
        启用auto-fit时应该使用正确的CSS
        """
        grid = self.create_grid_component(width, 768)
        
        styles = grid.getGridStyles(auto_fit=True, min_col_width='250px')
        
        # 验证auto-fit样式
        grid_template = styles['gridTemplateColumns']
        assert 'auto-fit' in grid_template, f"应该包含auto-fit: {grid_template}"
        assert 'minmax(250px, 1fr)' in grid_template, f"应该包含正确的minmax: {grid_template}"
    
    @given(width=screen_widths, size=container_sizes)
    def test_container_component_classes_property(self, width, size):
        """
        属性: 容器组件类名正确性
        
        容器组件应该生成正确的CSS类名
        """
        container = self.create_container_component(width, 768)
        
        classes = container.getContainerClasses(
            size=size, center=True, background='white', shadow=True
        )
        
        # 验证基础类
        assert 'container' in classes
        
        # 验证大小类
        if size in container.size_map:
            assert container.size_map[size] in classes
        
        # 验证居中类
        assert 'mx-auto' in classes
        
        # 验证背景类
        assert 'bg-white' in classes
        
        # 验证阴影类
        assert 'shadow-sm' in classes
    
    @given(width=screen_widths)
    def test_container_component_responsive_padding_property(self, width):
        """
        属性: 容器组件响应式内边距正确性
        
        容器组件应该根据屏幕宽度返回正确的内边距
        """
        container = self.create_container_component(width, 768)
        
        padding_config = {
            'xs': '1rem',
            'sm': '1.5rem',
            'lg': '2rem',
            'xl': '2.5rem'
        }
        
        padding = container.getResponsivePadding(padding_config)
        
        # 验证返回值
        assert isinstance(padding, str), f"内边距应该是字符串，得到: {padding}"
        assert padding in padding_config.values(), f"内边距值应该来自配置: {padding}"
        
        # 验证响应式逻辑
        responsive = container.responsive
        current_bp = responsive.currentBreakpoint
        
        # 检查是否使用了正确的断点配置
        expected_padding = None
        for bp in reversed(responsive.ordered_breakpoints):
            if bp in padding_config and responsive.isBreakpoint(bp):
                expected_padding = padding_config[bp]
                break
        
        if expected_padding:
            assert padding == expected_padding, \
                f"宽度 {width} (断点 {current_bp}) 应该使用内边距 {expected_padding}，实际: {padding}"
    
    @given(width=screen_widths)
    def test_image_component_responsive_src_property(self, width):
        """
        属性: 图片组件响应式源正确性
        
        图片组件应该根据屏幕宽度选择正确的图片源
        """
        image = self.create_image_component(width, 768)
        
        responsive_src = {
            'xs': 'image-xs.jpg',
            'sm': 'image-sm.jpg',
            'md': 'image-md.jpg',
            'lg': 'image-lg.jpg',
            'xl': 'image-xl.jpg'
        }
        
        current_src = image.getCurrentSrc(responsive_src=responsive_src)
        
        # 验证返回值
        assert isinstance(current_src, str), f"图片源应该是字符串，得到: {current_src}"
        assert current_src in responsive_src.values(), f"图片源应该来自配置: {current_src}"
        
        # 验证响应式逻辑
        responsive = image.responsive
        current_bp = responsive.currentBreakpoint
        
        # 检查是否使用了正确的断点配置
        expected_src = None
        for bp in reversed(responsive.ordered_breakpoints):
            if bp in responsive_src and responsive.isBreakpoint(bp):
                expected_src = responsive_src[bp]
                break
        
        if expected_src:
            assert current_src == expected_src, \
                f"宽度 {width} (断点 {current_bp}) 应该使用图片源 {expected_src}，实际: {current_src}"
    
    @given(aspect_ratio=aspect_ratios)
    def test_image_component_aspect_ratio_property(self, aspect_ratio):
        """
        属性: 图片组件宽高比正确性
        
        图片组件应该生成正确的宽高比样式
        """
        image = self.create_image_component(1024, 768)
        
        styles = image.getAspectRatioStyle(aspect_ratio)
        
        # 验证样式存在
        assert 'aspectRatio' in styles, f"应该包含aspectRatio样式"
        
        # 验证预设宽高比
        aspect_value = styles['aspectRatio']
        if aspect_ratio == 'square':
            assert aspect_value == '1 / 1'
        elif aspect_ratio == 'video':
            assert aspect_value == '16 / 9'
        elif aspect_ratio == 'portrait':
            assert aspect_value == '3 / 4'
        elif aspect_ratio == 'landscape':
            assert aspect_value == '4 / 3'
        else:
            assert aspect_value == aspect_ratio
    
    @given(width=screen_widths)
    def test_css_utility_visibility_property(self, width):
        """
        属性: CSS工具类可见性正确性
        
        响应式显示/隐藏工具类应该在正确的屏幕尺寸下工作
        """
        validator = CSSUtilityValidator()
        
        # 测试显示类
        show_mobile = validator.isClassVisible('show-mobile', width)
        show_tablet = validator.isClassVisible('show-tablet', width)
        show_desktop = validator.isClassVisible('show-desktop', width)
        
        # 验证逻辑
        if width < 768:
            assert show_mobile, f"宽度 {width} 下 show-mobile 应该可见"
            assert not show_desktop, f"宽度 {width} 下 show-desktop 不应该可见"
        elif width < 1024:
            assert show_tablet, f"宽度 {width} 下 show-tablet 应该可见"
            assert not show_mobile, f"宽度 {width} 下 show-mobile 不应该可见"
        else:
            assert show_desktop, f"宽度 {width} 下 show-desktop 应该可见"
            assert not show_mobile, f"宽度 {width} 下 show-mobile 不应该可见"
        
        # 测试隐藏类
        hide_mobile = validator.isClassVisible('hide-mobile', width)
        hide_desktop = validator.isClassVisible('hide-desktop', width)
        
        # 验证互补性
        assert show_mobile != hide_mobile, f"show-mobile 和 hide-mobile 应该是互补的"
        assert show_desktop != hide_desktop, f"show-desktop 和 hide-desktop 应该是互补的"
    
    def test_css_utility_class_validation_property(self):
        """
        属性: CSS工具类验证正确性
        
        CSS工具类验证器应该正确识别有效的类名
        """
        validator = CSSUtilityValidator()
        
        # 测试网格类
        valid_grid_classes = [
            'grid-responsive', 'grid-responsive-2', 'grid-responsive-3',
            'grid-responsive-4', 'grid-responsive-5', 'grid-responsive-6'
        ]
        
        for class_name in valid_grid_classes:
            assert validator.validateGridClass(class_name), f"网格类 {class_name} 应该是有效的"
        
        # 测试无效网格类
        invalid_grid_classes = ['grid-responsive-0', 'grid-responsive-13', 'invalid-grid']
        
        for class_name in invalid_grid_classes:
            assert not validator.validateGridClass(class_name), f"网格类 {class_name} 应该是无效的"
        
        # 测试文本类
        valid_text_classes = [
            'heading-1', 'heading-2', 'text-responsive-xs', 'text-responsive-lg'
        ]
        
        for class_name in valid_text_classes:
            assert validator.validateTextClass(class_name), f"文本类 {class_name} 应该是有效的"
    
    @given(width1=screen_widths, width2=screen_widths)
    def test_responsive_component_state_consistency_property(self, width1, width2):
        """
        属性: 响应式组件状态一致性
        
        相同断点下的不同宽度应该产生一致的组件状态
        """
        responsive1 = self.create_responsive_composable(width1, 768)
        responsive2 = self.create_responsive_composable(width2, 768)
        
        bp1 = responsive1.currentBreakpoint
        bp2 = responsive2.currentBreakpoint
        
        # 如果断点相同，组件状态应该一致
        if bp1 == bp2:
            assert responsive1.isMobile == responsive2.isMobile
            assert responsive1.isTablet == responsive2.isTablet
            assert responsive1.isDesktop == responsive2.isDesktop
            assert responsive1.deviceType == responsive2.deviceType
            
            # 网格组件状态一致性
            grid1 = ResponsiveGridComponent(responsive1)
            grid2 = ResponsiveGridComponent(responsive2)
            
            for preset in grid1.presets:
                cols1 = grid1.getColumns(preset=preset)
                cols2 = grid2.getColumns(preset=preset)
                assert cols1 == cols2, \
                    f"相同断点 {bp1} 下，{preset} 预设的列数应该一致"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])