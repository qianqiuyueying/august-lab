import AdmZip from "adm-zip";

// 允许的扩展名白名单（小写）
export const ALLOWED_EXTENSIONS = new Set([
  ".html", ".htm", ".xhtml",
  ".css", ".scss", ".less",
  ".js", ".mjs", ".ts", ".json", ".jsx", ".tsx",
  ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp", ".avif",
  ".woff", ".woff2", ".ttf", ".otf", ".eot",
  ".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac",
  ".mp4", ".webm", ".ogv", ".avi", ".mov",
  ".wasm",
  ".csv", ".xml", ".txt", ".md", ".yaml", ".yml", ".toml",
  ".pbf", ".mvt",
  ".gltf", ".glb", ".bin", ".dat",
]);

export const MAX_ZIP_SIZE = 50 * 1024 * 1024;
export const MAX_EXTRACTED_SIZE = 100 * 1024 * 1024;

export interface ValidationResult {
  ok: boolean;
  error?: string;
}

export function validatePackage(zipBuffer: Buffer, slug: string): ValidationResult {
  let zip: AdmZip;

  try {
    zip = new AdmZip(zipBuffer);
  } catch {
    return { ok: false, error: "无效的 zip 文件" };
  }

  const entries = zip.getEntries();
  if (entries.length === 0) {
    return { ok: false, error: "zip 文件为空" };
  }

  // 检查解压后总大小
  const totalSize = entries.reduce((sum, e) => sum + (e.header.size || 0), 0);
  if (totalSize > MAX_EXTRACTED_SIZE) {
    return {
      ok: false,
      error: `解压后总大小 ${(totalSize / 1024 / 1024).toFixed(1)}MB 超过限制 ${MAX_EXTRACTED_SIZE / 1024 / 1024}MB`,
    };
  }

  // 检查根目录是否有 index.html
  const rootNames = new Set(
    entries.filter((e) => !e.isDirectory && !e.entryName.includes("/")).map((e) => e.entryName.toLowerCase())
  );
  if (!rootNames.has("index.html")) {
    return { ok: false, error: "zip 根目录必须包含 index.html" };
  }

  // 检查所有文件后缀名
  for (const entry of entries) {
    if (entry.isDirectory) continue;
    const name = entry.entryName.toLowerCase();
    const lastDot = name.lastIndexOf(".");
    const ext = lastDot === -1 ? "" : name.slice(lastDot);
    if (!ext || !ALLOWED_EXTENSIONS.has(ext)) {
      return { ok: false, error: `不允许的文件类型: ${entry.entryName}` };
    }
  }

  return { ok: true };
}

export function extractPackage(zipBuffer: Buffer, targetDir: string): void {
  const zip = new AdmZip(zipBuffer);
  zip.extractAllTo(targetDir, true);
}
