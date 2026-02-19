// app/api/chat/route.ts
import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

export async function POST(req: Request) {
  try {
    const { message } = await req.json();

    // We use gemini-1.5-flash as it is extremely fast and perfect for voice conversations
    const model = genAI.getGenerativeModel({ model: "gemini-flash-latest" });
    
    // Prompting it to give short, conversational answers suited for voice
    const prompt = `You are a helpful, friendly voice assistant. Keep your answers concise, conversational, and natural to read aloud. The user says: "${message}"`;

    const result = await model.generateContent(prompt);
    const text = result.response.text();

    return NextResponse.json({ text });
  } catch (error) {
    console.error("Gemini API Error:", error);
    return NextResponse.json(
      { error: "Failed to generate response" },
      { status: 500 }
    );
  }
}