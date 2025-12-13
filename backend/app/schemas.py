from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator, HttpUrl
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
import re
from .validators import (
    validate_url, validate_github_url, validate_linkedin_url, validate_twitter_url,
    validate_tech_stack_item, validate_tag, validate_display_order, validate_skill_level,
    validate_markdown_content
)

# 作品相关模型
class PortfolioBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="作品标题")
    description: Optional[str] = Field(None, max_length=2000, description="作品描述")
    tech_stack: List[str] = Field(default_factory=list, max_items=20, description="技术栈列表")
    project_url: Optional[Union[HttpUrl, str]] = Field(None, description="项目链接")
    github_url: Optional[Union[HttpUrl, str]] = Field(None, description="GitHub链接")
    image_url: Optional[Union[HttpUrl, str]] = Field(None, description="封面图片链接")
    display_order: int = Field(0, ge=0, le=9999, description="显示顺序")
    is_featured: bool = Field(False, description="是否为推荐作品")
    
    @validator('tech_stack')
    def validate_tech_stack(cls, v):
        if v:
            return [validate_tech_stack_item(tech) for tech in v if tech and tech.strip()]
        return []
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('标题不能为空')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @validator('project_url', 'github_url', 'image_url')
    def validate_portfolio_urls(cls, v):
        return validate_url(v)

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    project_url: Optional[str] = None
    github_url: Optional[str] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = None
    is_featured: Optional[bool] = None

class Portfolio(PortfolioBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime

# 博客相关模型
class BlogBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="博客标题")
    content: str = Field(..., min_length=1, max_length=50000, description="博客内容")
    summary: Optional[str] = Field(None, max_length=1000, description="博客摘要")
    tags: List[str] = Field(default_factory=list, max_items=10, description="标签列表")
    is_published: bool = Field(False, description="是否已发布")
    cover_image: Optional[Union[HttpUrl, str]] = Field(None, description="封面图片链接")
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            return [validate_tag(tag) for tag in v if tag and tag.strip()]
        return []
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('标题不能为空')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        return validate_markdown_content(v)
    
    @validator('summary')
    def validate_summary(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @validator('cover_image')
    def validate_cover_image_url(cls, v):
        return validate_url(v)

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    cover_image: Optional[str] = None

class Blog(BlogBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

# 个人信息相关模型
class Skill(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="技能名称")
    level: int = Field(..., ge=0, le=100, description="技能熟练度(0-100)")
    category: str = Field(..., min_length=1, max_length=50, description="技能分类")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('技能名称不能为空')
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        if not v or not v.strip():
            raise ValueError('技能分类不能为空')
        # 限制分类选项
        allowed_categories = ['frontend', 'backend', 'database', 'tools', 'other']
        category = v.strip().lower()
        if category not in allowed_categories:
            raise ValueError(f'技能分类必须是以下之一: {", ".join(allowed_categories)}')
        return category
    
    @validator('level')
    def validate_level(cls, v):
        return validate_skill_level(v)

class ProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    title: Optional[str] = Field(None, max_length=200, description="职位/头衔")
    bio: Optional[str] = Field(None, max_length=5000, description="个人简介")
    avatar_url: Optional[Union[HttpUrl, str]] = Field(None, description="头像链接")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    github_url: Optional[Union[HttpUrl, str]] = Field(None, description="GitHub链接")
    linkedin_url: Optional[Union[HttpUrl, str]] = Field(None, description="LinkedIn链接")
    twitter_url: Optional[Union[HttpUrl, str]] = Field(None, description="Twitter链接")
    skills: List[Skill] = Field(default_factory=list, max_items=50, description="技能列表")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('姓名不能为空')
        return v.strip()
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @validator('bio')
    def validate_bio(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @validator('github_url')
    def validate_github_url_field(cls, v):
        return validate_github_url(v)
    
    @validator('linkedin_url')
    def validate_linkedin_url_field(cls, v):
        return validate_linkedin_url(v)
    
    @validator('twitter_url')
    def validate_twitter_url_field(cls, v):
        return validate_twitter_url(v)
    
    @validator('avatar_url')
    def validate_avatar_url_field(cls, v):
        return validate_url(v)

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    skills: Optional[List[Skill]] = None

class Profile(ProfileBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    updated_at: datetime

# 认证相关模型
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# 产品相关模型
class ProductBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="产品标题")
    description: Optional[str] = Field(None, max_length=2000, description="产品描述")
    tech_stack: List[str] = Field(default_factory=list, max_items=20, description="技术栈列表")
    product_type: str = Field(..., description="产品类型")
    entry_file: str = Field("index.html", max_length=200, description="入口文件")
    config_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="产品配置")
    is_published: bool = Field(False, description="是否已发布")
    is_featured: bool = Field(False, description="是否为推荐产品")
    display_order: int = Field(0, ge=0, le=9999, description="显示顺序")
    version: str = Field("1.0.0", max_length=50, description="产品版本")
    
    @validator('tech_stack')
    def validate_tech_stack(cls, v):
        if v:
            return [validate_tech_stack_item(tech) for tech in v if tech and tech.strip()]
        return []
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('产品标题不能为空')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @validator('product_type')
    def validate_product_type(cls, v):
        allowed_types = ['static', 'spa', 'game', 'tool']
        if v not in allowed_types:
            raise ValueError(f'产品类型必须是以下之一: {", ".join(allowed_types)}')
        return v
    
    @validator('entry_file')
    def validate_entry_file(cls, v):
        if not v or not v.strip():
            raise ValueError('入口文件不能为空')
        # 简单的文件名验证
        if not re.match(r'^[a-zA-Z0-9._-]+\.(html|htm)$', v.strip()):
            raise ValueError('入口文件必须是有效的HTML文件名')
        return v.strip()

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    product_type: Optional[str] = None
    entry_file: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None
    version: Optional[str] = None

class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ProductStatsBase(BaseModel):
    product_id: int
    visitor_ip: Optional[str] = None
    session_id: Optional[str] = None
    duration_seconds: int = Field(0, ge=0, description="使用时长(秒)")
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

class ProductStatsCreate(ProductStatsBase):
    pass

class ProductStats(ProductStatsBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    access_time: datetime

class ProductLogBase(BaseModel):
    product_id: int
    log_type: str = Field(..., description="日志类型")
    log_level: str = Field("info", description="日志级别")
    message: str = Field(..., min_length=1, description="日志消息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    
    @validator('log_type')
    def validate_log_type(cls, v):
        allowed_types = ['access', 'error', 'performance', 'security']
        if v not in allowed_types:
            raise ValueError(f'日志类型必须是以下之一: {", ".join(allowed_types)}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['debug', 'info', 'warning', 'error']
        if v not in allowed_levels:
            raise ValueError(f'日志级别必须是以下之一: {", ".join(allowed_levels)}')
        return v

class ProductLogCreate(ProductLogBase):
    pass

class ProductLog(ProductLogBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    timestamp: datetime

class ProductUploadResponse(BaseModel):
    message: str
    product_id: int
    file_path: str
    extracted_files: List[str]

class ProductAnalytics(BaseModel):
    product_id: int
    total_visits: int
    unique_visitors: int
    average_duration: float
    last_access: Optional[datetime]
    popular_times: List[Dict[str, Any]]

# 产品反馈相关模型
class ProductFeedbackBase(BaseModel):
    product_id: int
    user_name: Optional[str] = Field(None, max_length=100, description="用户姓名")
    user_email: Optional[EmailStr] = Field(None, description="用户邮箱")
    feedback_type: str = Field(..., description="反馈类型")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5星)")
    title: str = Field(..., min_length=1, max_length=200, description="反馈标题")
    content: str = Field(..., min_length=1, max_length=5000, description="反馈内容")
    
    @validator('feedback_type')
    def validate_feedback_type(cls, v):
        allowed_types = ['bug', 'feature', 'improvement', 'general']
        if v not in allowed_types:
            raise ValueError(f'反馈类型必须是以下之一: {", ".join(allowed_types)}')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('反馈标题不能为空')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('反馈内容不能为空')
        return v.strip()
    
    @validator('user_name')
    def validate_user_name(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v

class ProductFeedbackCreate(ProductFeedbackBase):
    pass

class ProductFeedbackUpdate(BaseModel):
    status: Optional[str] = None
    admin_reply: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'reviewed', 'resolved', 'closed']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v
    
    @validator('admin_reply')
    def validate_admin_reply(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v

class ProductFeedback(ProductFeedbackBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    admin_reply: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    replied_at: Optional[datetime] = None

class ProductFeedbackStats(BaseModel):
    product_id: int
    total_feedback: int
    average_rating: Optional[float]
    feedback_by_type: Dict[str, int]
    feedback_by_status: Dict[str, int]
    recent_feedback: List[ProductFeedback]

# 扩展管理相关模型
class ExtensionInstallRequest(BaseModel):
    path: str = Field(..., min_length=1, description="扩展路径或URL")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="扩展配置")

class ExtensionConfigureRequest(BaseModel):
    config: Dict[str, Any] = Field(..., description="扩展配置")

# 通用响应模型
class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime