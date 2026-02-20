// app/api/tts/route.ts
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { text } = await req.json();
    
    // 'Rachel' voice ID
    const voiceId = "21m00Tcm4TlvDq8ikWAM"; 

    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "xi-api-key": process.env.ELEVENLABS_API_KEY || "", // Fallback to empty string to prevent crashes
        },
        body: JSON.stringify({
          text,
          model_id: "eleven_turbo_v2", 
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75,
          },
        }),
      }
    );

    if (!response.ok) {
      const errorData = await response.json(); // Read the actual error from ElevenLabs
      console.error("🚨 ElevenLabs Detailed Error:", errorData);
      throw new Error(`ElevenLabs API rejected the request: ${response.status}`);
    }

    const audioBuffer = await response.arrayBuffer();
    return new NextResponse(audioBuffer, {
      headers: { "Content-Type": "audio/mpeg" },
    });
  } catch (error) {
    console.error("ElevenLabs API Error:", error);
    return NextResponse.json({ error: "TTS failed" }, { status: 500 });
  }
}