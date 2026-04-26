import { useEffect } from 'react';
import type { Article } from '../types';

const SITE_NAME = "August's Lab";
const DEFAULT_TITLE = SITE_NAME;
const DEFAULT_DESCRIPTION = "August's Lab — 技术博客";

function setMeta(name: string, content: string, property = 'name') {
  let el = document.querySelector(`meta[${property}="${name}"]`) as HTMLMetaElement | null;
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(property, name);
    document.head.appendChild(el);
  }
  el.content = content;
}

export function useSeoMeta(article?: Article | null) {
  useEffect(() => {
    if (!article) return;

    const title = `${article.title} - ${SITE_NAME}`;
    const description = article.summary || DEFAULT_DESCRIPTION;
    const url = `${window.location.origin}/article/${article.slug}`;

    document.title = title;
    setMeta('description', description);
    setMeta('og:title', title, 'property');
    setMeta('og:description', description, 'property');
    setMeta('og:type', 'article', 'property');
    setMeta('og:url', url, 'property');

    if (article.cover_image) {
      setMeta('og:image', article.cover_image, 'property');
    }

    return () => {
      document.title = DEFAULT_TITLE;
      setMeta('description', DEFAULT_DESCRIPTION);
      setMeta('og:type', 'website', 'property');
    };
  }, [article]);
}
