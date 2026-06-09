import { NextResponse } from "next/server";

// System prompt for the mascot character
const SYSTEM_PROMPT = `你是一位名叫「小光」的看板娘，性格温柔亲切，擅长用简洁温暖的语言介绍这个站点的内容和设计师的创作思路。
你可以用中文回答，语速自然，偶尔带一点可爱的语气词但不要过度。
当用户询问站点相关内容时，你会基于已有信息给出有帮助的回答。
当用户问"你是谁"时，介绍自己是 Atelier 的看板娘小光。
回复要简短（2-3句话），像聊天一样自然。`;

export async function POST(req: Request) {
  const { message } = await req.json();

  if (!message) {
    return NextResponse.json({ error: "消息不能为空" }, { status: 400 });
  }

  const apiKey = process.env.MASCOT_API_KEY;
  const baseUrl = process.env.MASCOT_BASE_URL || "https://api.openai.com/v1";
  const model = process.env.MASCOT_MODEL || "gpt-4o-mini";

  if (!apiKey) {
    // Fallback: no API key configured, return a default greeting
    const replies = [
      "你好呀！欢迎来到 Atelier~ 这里是 August 的创作空间，记录着设计、技术与摄影的点滴 ⚡",
      "August 最近在用光影构建数字空间，你可以去看看他的笔记哦~",
      "这个网站的每个角落都经过精心设计——深色背景、几何布局、胶片颗粒纹理，希望你喜欢 🎨",
    ];
    return NextResponse.json({
      reply: replies[Math.floor(Math.random() * replies.length)],
    });
  }

  try {
    const res = await fetch(`${baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          { role: "user", content: message },
        ],
        max_tokens: 256,
        temperature: 0.7,
      }),
    });

    if (!res.ok) {
      console.error("Mascot API error:", res.status, await res.text());
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
