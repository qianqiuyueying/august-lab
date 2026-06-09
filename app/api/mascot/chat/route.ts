import { NextResponse } from "next/server";
import { prisma } from "@/lib/db";

export async function POST(req: Request) {
  const { message } = await req.json();
  if (!message) return NextResponse.json({ error: "消息不能为空" }, { status: 400 });

  // Read settings from DB
  let settings = await prisma.mascotSettings.findFirst({ where: { id: 1 } });
  if (!settings) {
    settings = await prisma.mascotSettings.create({ data: { id: 1 } });
  }

  // Fallback: no API key, return preset reply
  if (!settings.apiKey) {
    const replies = [
      "你好呀！欢迎来到 Atelier~ 这里是 August 的创作空间，记录着设计、技术与摄影的点滴 ⚡",
      "August 最近在用光影构建数字空间，你可以去看看他的笔记哦~",
      "这个网站的每个角落都经过精心设计——深色背景、几何布局、胶片颗粒纹理，希望你喜欢 🎨",
    ];
    return NextResponse.json({ reply: replies[Math.floor(Math.random() * replies.length)] });
  }

  try {
    const res = await fetch(`${settings.baseUrl}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${settings.apiKey}` },
      body: JSON.stringify({
        model: settings.model,
        messages: [
          { role: "system", content: settings.person },
          { role: "user", content: message },
        ],
        max_tokens: settings.maxTokens,
        temperature: settings.temperature,
      }),
    });

    if (!res.ok) {
      console.error("Mascot API error:", res.status);
      return NextResponse.json({ reply: "呜...脑子有点乱，待会再聊吧 (´•ω•`)" });
    }

    const data = await res.json();
    const reply = data.choices?.[0]?.message?.content || "嗯嗯，我明白了~";
    return NextResponse.json({ reply });
  } catch (err) {
    console.error("Mascot chat error:", err);
    return NextResponse.json({ reply: "呜...脑子有点乱，待会再聊吧 (´•ω•`)" });
  }
}
