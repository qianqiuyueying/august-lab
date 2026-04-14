import { useState, useEffect } from 'react';
import { getComments, createComment } from '../api/comments';
import type { Comment } from '../types';

export function useComments(articleId: number) {
  const [data, setData] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!articleId) return;
    getComments(articleId)
      .then(setData)
      .finally(() => setLoading(false));
  }, [articleId]);

  const addComment = async (comment: { author_name: string; author_email: string; content: string }) => {
    const newComment = await createComment(articleId, comment);
    setData((prev) => [...prev, newComment]);
    return newComment;
  };

  return { data, loading, addComment };
}
