from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.article import Article
from app.models.comment import Comment
from app.dependencies import get_current_user
from app.schemas.comment import CommentCreate, CommentOut

router = APIRouter()


@router.get("/articles/{article_id}/comments", response_model=list[CommentOut])
async def list_comments(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Comment)
        .where(Comment.article_id == article_id)
        .order_by(Comment.created_at)
    )
    return result.scalars().all()


@router.post(
    "/articles/{article_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    article_id: int,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Article).where(Article.id == article_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Article not found")
    comment = Comment(
        article_id=article_id,
        author_name=data.author_name,
        author_email=data.author_email,
        content=data.content,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    await db.delete(comment)
    await db.commit()
