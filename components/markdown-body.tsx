import { MarkdownRenderer } from "@/lib/markdown";

interface MarkdownBodyProps {
  content: string;
}

export function MarkdownBody({ content }: MarkdownBodyProps) {
  return (
    <MarkdownRenderer
      content={content}
    />
  );
}
