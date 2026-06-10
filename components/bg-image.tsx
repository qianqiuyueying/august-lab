import Image from "next/image";

interface BgImageProps {
  src: string;
  alt: string;
  priority?: boolean;
  /** parallax speed, passed to data-parallax attribute */
  parallax?: string;
}

export function BgImage({ src, alt, priority = false, parallax }: BgImageProps) {
  return (
    <div className="home-section__bg" data-parallax={parallax}>
      <Image
        src={src}
        alt={alt}
        fill
        sizes="100vw"
        priority={priority}
        quality={82}
        style={{ objectFit: "cover" }}
      />
    </div>
  );
}
