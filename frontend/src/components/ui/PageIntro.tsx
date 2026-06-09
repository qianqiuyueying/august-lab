import type { ReactNode } from 'react';

interface PageIntroProps {
  eyebrow: string;
  title: string;
  description?: string;
  align?: 'left' | 'center';
  children?: ReactNode;
}

export default function PageIntro({ eyebrow, title, description, align = 'left', children }: PageIntroProps) {
  const centered = align === 'center';

  return (
    <header className={centered ? 'mx-auto max-w-3xl text-center' : 'max-w-3xl'}>
      <p className="section-label mb-3">{eyebrow}</p>
      <h1 className="text-4xl font-extrabold leading-[1.08] text-text-primary sm:text-5xl">
        {title}
      </h1>
      {description && (
        <p className={`mt-5 text-base leading-8 text-text-secondary sm:text-lg ${centered ? 'mx-auto max-w-2xl' : 'max-w-2xl'}`}>
          {description}
        </p>
      )}
      {children && <div className={centered ? 'mt-7 flex justify-center' : 'mt-7'}>{children}</div>}
    </header>
  );
}
