// app/api/tts/route.ts
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { text } = await req.json();
    
    // 'Rachel' voice ID from ElevenLabs. You can find more IDs in their documentation.
    const voiceId = "21m00Tcm4TlvDq8ikWAM"; 

    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "xi-api-key": process.env.ELEVENLABS_API_KEY!,
        },
        body: JSON.stringify({
          text,
          model_id: "eleven_turbo_v2", // Turbo model is fastest for real-time chat
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75,
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to generate audio from ElevenLabs");
    }

    // Return the audio stream directly to the client
    const audioBuffer = await response.arrayBuffer();
    return new NextResponse(audioBuffer, {
      headers: { "Content-Type": "audio/mpeg" },
    });
  } catch (error) {
    console.error("ElevenLabs API Error:", error);
    return NextResponse.json({ error: "TTS failed" }, { status: 500 });
  }
}