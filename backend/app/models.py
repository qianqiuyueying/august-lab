from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Index, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Portfolio(Base):
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    tech_stack = Column(JSON, default=list)  # 存储技术栈数组
    project_url = Column(String(500))
    github_url = Column(String(500))
    image_url = Column(String(500))
    display_order = Column(Integer, default=0, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 复合索引：按显示顺序和创建时间排序
    __table_args__ = (
        Index('idx_portfolio_order_created', 'display_order', 'created_at'),
        Index('idx_portfolio_featured_created', 'is_featured', 'created_at'),
    )

class Blog(Base):
    __tablename__ = "blog"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    tags = Column(JSON, default=list)  # 存储标签数组
    is_published = Column(Boolean, default=False, index=True)
    cover_image = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), index=True)
    
    # 复合索引：已发布文章按发布时间排序
    __table_args__ = (
        Index('idx_blog_published_date', 'is_published', 'published_at'),
        Index('idx_blog_published_created', 'is_published', 'created_at'),
    )

class Profile(Base):
    __tablename__ = "profile"
    
    id = Column(Integer, primary_key=True, default=1)
    name = Column(String(100), nullable=False)
    title = Column(String(200))
    bio = Column(Text)
    avatar_url = Column(String(500))
    email = Column(String(100), unique=True)  # 邮箱唯一约束
    github_url = Column(String(500))
    linkedin_url = Column(String(500))
    twitter_url = Column(String(500))
    skills = Column(JSON, default=list)  # 存储技能数组
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(50), default="admin", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # 复合索引：查找活跃且未过期的会话
    __table_args__ = (
        Index('idx_session_active_expires', 'is_active', 'expires_at'),
        Index('idx_session_user_active', 'user_id', 'is_active'),
    )

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    tech_stack = Column(JSON, default=list)  # 存储技术栈数组
    product_type = Column(String(50), nullable=False, index=True)  # 'static', 'spa', 'game', 'tool'
    entry_file = Column(String(200), default='index.html')
    file_path = Column(String(500))  # 产品文件存储路径
    config_data = Column(JSON, default=dict)  # 存储产品配置
    is_published = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    display_order = Column(Integer, default=0, index=True)
    version = Column(String(50), default='1.0.0')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 复合索引：按发布状态和显示顺序排序
    __table_args__ = (
        Index('idx_product_published_order', 'is_published', 'display_order'),
        Index('idx_product_featured_created', 'is_featured', 'created_at'),
        Index('idx_product_type_published', 'product_type', 'is_published'),
    )

class ProductStats(Base):
    __tablename__ = "product_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    visitor_ip = Column(String(45))
    session_id = Column(String(100))
    access_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    duration_seconds = Column(Integer, default=0)
    user_agent = Column(Text)
    referrer = Column(String(500))
    
    # 复合索引：按产品和访问时间排序
    __table_args__ = (
        Index('idx_product_stats_product_time', 'product_id', 'access_time'),
        Index('idx_product_stats_ip_time', 'visitor_ip', 'access_time'),
    )

class ProductLog(Base):
    __tablename__ = "product_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    log_type = Column(String(50), nullable=False, index=True)  # 'access', 'error', 'performance'
    log_level = Column(String(20), default='info', index=True)  # 'debug', 'info', 'warning', 'error'
    message = Column(Text, nullable=False)
    details = Column(JSON)  # 存储详细信息
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 复合索引：按产品、日志类型和时间排序
    __table_args__ = (
        Index('idx_product_logs_product_type', 'product_id', 'log_type'),
        Index('idx_product_logs_level_time', 'log_level', 'timestamp'),
        Index('idx_product_logs_product_time', 'product_id', 'timestamp'),
    )

class ProductFeedback(Base):
    __tablename__ = "product_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    user_name = Column(String(100))  # 可选的用户名
    user_email = Column(String(100))  # 可选的用户邮箱
    feedback_type = Column(String(50), nullable=False, index=True)  # 'bug', 'feature', 'improvement', 'general'
    rating = Column(Integer)  # 1-5星评分
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default='pending', index=True)  # 'pending', 'reviewed', 'resolved', 'closed'
    admin_reply = Column(Text)  # 管理员回复
    user_agent = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    replied_at = Column(DateTime(timezone=True))  # 回复时间
    
    # 复合索引：按产品、状态和创建时间排序
    __table_args__ = (
        Index('idx_feedback_product_status', 'product_id', 'status'),
        Index('idx_feedback_type_created', 'feedback_type', 'created_at'),
        Index('idx_feedback_status_created', 'status', 'created_at'),
        Index('idx_feedback_rating_created', 'rating', 'created_at'),
    )

class ProductAPIToken(Base):
    __tablename__ = "product_api_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    permissions = Column(JSON, default=list)  # 存储权限列表
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_used_at = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
    
    # 复合索引：按产品和状态排序
    __table_args__ = (
        Index('idx_api_token_product_active', 'product_id', 'is_active'),
        Index('idx_api_token_expires', 'expires_at'),
    )

class ProductAPICall(Base):
    __tablename__ = "product_api_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    token_id = Column(Integer, ForeignKey('product_api_tokens.id', ondelete='SET NULL'), index=True)
    endpoint = Column(String(500), nullable=False, index=True)
    method = Column(String(10), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    response_time = Column(Integer)  # 响应时间（毫秒）
    request_size = Column(Integer)  # 请求大小（字节）
    response_size = Column(Integer)  # 响应大小（字节）
    error_message = Column(Text)
    client_ip = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 复合索引：按产品、时间和状态排序
    __table_args__ = (
        Index('idx_api_call_product_time', 'product_id', 'timestamp'),
        Index('idx_api_call_status_time', 'status_code', 'timestamp'),
        Index('idx_api_call_endpoint_time', 'endpoint', 'timestamp'),
    )

class ProductDataStorage(Base):
    __tablename__ = "product_data_storage"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    storage_key = Column(String(255), nullable=False, index=True)
    storage_value = Column(JSON)  # 存储JSON数据
    data_type = Column(String(50), default='json', index=True)  # 'json', 'text', 'binary'
    size_bytes = Column(Integer, default=0)
    is_encrypted = Column(Boolean, default=False)
    access_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    accessed_at = Column(DateTime(timezone=True))
    
    # 复合索引：按产品和键排序
    __table_args__ = (
        Index('idx_data_storage_product_key', 'product_id', 'storage_key'),
        Index('idx_data_storage_type_size', 'data_type', 'size_bytes'),
    )

class ProductUser(Base):
    __tablename__ = "product_users"
    
    id = Column(String(100), primary_key=True, index=True)  # UUID格式
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    username = Column(String(100), index=True)
    email = Column(String(255), index=True)
    display_name = Column(String(200))
    avatar_url = Column(String(500))
    preferences = Column(JSON, default=dict)  # 存储用户偏好设置
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True))
    
    # 复合索引：按产品和用户名排序
    __table_args__ = (
        Index('idx_product_user_username', 'product_id', 'username'),
        Index('idx_product_user_email', 'product_id', 'email'),
        Index('idx_product_user_active', 'product_id', 'is_active'),
    )

class ProductUserSession(Base):
    __tablename__ = "product_user_sessions"
    
    id = Column(String(100), primary_key=True, index=True)  # UUID格式
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(String(100), ForeignKey('product_users.id', ondelete='CASCADE'), index=True)
    session_data = Column(JSON, default=dict)  # 存储会话数据
    is_guest = Column(Boolean, default=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_accessed_at = Column(DateTime(timezone=True))
    
    # 复合索引：按产品、用户和过期时间排序
    __table_args__ = (
        Index('idx_session_product_user', 'product_id', 'user_id'),
        Index('idx_session_expires', 'expires_at'),
        Index('idx_session_guest_expires', 'is_guest', 'expires_at'),
    )