"use client";

import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Loader2, Mic, Square } from "lucide-react";
import Image from "next/image";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export default function FullPageChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! How can I help you today? Type or click the mic to speak.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false); // Added recording state

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null); // Added speech recognition ref

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize Speech Recognition on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = "en-US";
      }
    }
  }, []);

  // ElevenLabs Text-to-Speech function
  const speakResponse = async (text: string) => {
    try {
      const response = await fetch("/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error("Audio fetch failed");

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.play();
    } catch (error) {
      console.error("Error playing audio:", error);
    }
  };

  // Main logic to handle messaging (both text and voice)
  const processMessage = async (
    text: string,
    isVoiceInput: boolean = false,
  ) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 1. Send text to Gemini API
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error);

      const replyText = data.text;

      // 2. Add Gemini's text response to the UI
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: replyText,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // 3. ONLY play the ElevenLabs audio if the user used the microphone
      if (isVoiceInput) {
        speakResponse(replyText);
      }
    } catch (error) {
      console.error("Failed to fetch response:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "assistant",
          content: "Sorry, I encountered an error connecting to the AI.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Triggered when user clicks Send or hits Enter
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    processMessage(input, false); // false = don't speak back
    setInput("");
  };

  // Triggered when user clicks the Microphone
  const toggleVoice = () => {
    if (!recognitionRef.current) {
      alert("Voice input isn't supported in this browser. Try Chrome or Edge.");
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      recognitionRef.current.onresult = (e: any) => {
        const transcript = e.results[0][0].transcript;
        if (transcript) {
          processMessage(transcript, true); // true = speak back via ElevenLabs!
        }
      };

      recognitionRef.current.onerror = (e: any) => {
        if (e.error !== "aborted")
          console.error("Speech recognition error:", e.error);
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  return (
    <div className="flex flex-col h-screen w-full bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Header */}
      <div className="border-b border-blue-200/50 bg-gradient-to-r from-white via-blue-50 to-white sticky top-0 z-10 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Logo with multiple color accent */}
            <div className="relative w-12 h-12 rounded-xl bg-gradient-to-br from-[#0460A9] via-[#E74A21] to-[#EC9A1E] p-1 overflow-hidden">
              <div className="relative w-full h-full rounded-lg bg-white flex items-center justify-center overflow-hidden">
                <Image
                  src="/placeholder-logo.png"
                  alt="AI Assistant Logo"
                  fill
                  style={{ objectFit: "cover" }}
                />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Assistant</h1>
              <p className="text-xs text-gray-500 font-medium">
                Your travel assistant
              </p>
            </div>
          </div>
          {isRecording && (
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-[#E74A21]/10 to-[#EC9A1E]/10 border border-[#E74A21]/30">
              <span className="w-2.5 h-2.5 rounded-full bg-gradient-to-r from-[#E74A21] to-[#EC9A1E] animate-pulse"></span>
              <span className="text-xs font-bold text-[#E74A21]">
                Listening...
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto bg-gradient-to-b from-slate-50 via-white to-blue-50/40">
        <div className="max-w-3xl mx-auto w-full px-6 py-8 space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-end gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300 ${
                message.role === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold text-white shadow-md ${
                  message.role === "user"
                    ? "bg-gradient-to-br from-[#0460A9] to-[#0350a1]"
                    : "bg-gradient-to-br from-[#EC9A1E] to-[#EA7220]"
                }`}
              >
                {message.role === "user" ? "You" : "AI"}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-xl text-sm leading-relaxed ${
                  message.role === "user"
                    ? "bg-gradient-to-br from-[#0460A9] to-[#0350a1] text-white px-6 py-4 rounded-3xl rounded-tr-lg shadow-lg shadow-blue-500/25 font-medium"
                    : "bg-white text-gray-900 px-6 py-4 rounded-3xl rounded-tl-lg border border-gray-200/60 shadow-md hover:shadow-lg hover:border-[#0460A9]/30 transition-all duration-200"
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-end gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-[#EC9A1E] to-[#EA7220] text-white flex items-center justify-center text-xs font-bold shadow-md">
                AI
              </div>
              <div className="bg-white border border-gray-200/60 text-gray-600 text-sm px-6 py-4 rounded-3xl rounded-tl-lg flex items-center gap-3 shadow-md">
                <div className="flex gap-1">
                  <div
                    className="w-2 h-2 rounded-full bg-gradient-to-r from-[#0460A9] to-[#EC9A1E] animate-bounce"
                    style={{ animationDelay: "0s" }}
                  ></div>
                  <div
                    className="w-2 h-2 rounded-full bg-gradient-to-r from-[#E74A21] to-[#EA7220] animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                  <div
                    className="w-2 h-2 rounded-full bg-gradient-to-r from-[#EC9A1E] to-[#0460A9] animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  ></div>
                </div>
                <span className="text-xs font-semibold">Thinking</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-blue-200/50 bg-gradient-to-t from-white via-blue-50 to-white backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-6 py-6 w-full">
          <form
            onSubmit={handleSubmit}
            className={`flex items-center gap-3 bg-white border-2 rounded-2xl px-5 py-3 transition-all duration-200 ${
              isRecording
                ? "border-[#E74A21] ring-2 ring-[#E74A21]/20 shadow-lg shadow-orange-500/20 bg-gradient-to-r from-white to-orange-50/30"
                : "border-gray-300 focus-within:border-[#0460A9] focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:shadow-xl focus-within:shadow-blue-500/15"
            }`}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                isRecording ? "Listening..." : "Type your message..."
              }
              disabled={isLoading || isRecording}
              className="flex-1 bg-transparent text-base placeholder:text-gray-400 text-gray-900 focus:outline-none disabled:opacity-50 font-medium"
            />

            {/* Microphone Button */}
            <button
              type="button"
              onClick={toggleVoice}
              disabled={isLoading}
              className={`p-2.5 rounded-xl transition-all duration-200 disabled:opacity-40 ${
                isRecording
                  ? "bg-gradient-to-br from-[#E74A21] to-[#EC9A1E] text-white shadow-lg shadow-orange-500/40 animate-pulse hover:shadow-orange-500/50"
                  : "text-gray-600 hover:text-[#0460A9] hover:bg-blue-50 active:bg-blue-100"
              }`}
              aria-label={isRecording ? "Stop recording" : "Start recording"}
            >
              {isRecording ? (
                <Square size={20} fill="currentColor" />
              ) : (
                <Mic size={20} />
              )}
            </button>

            {/* Send Text Button */}
            <button
              type="submit"
              disabled={!input.trim() || isLoading || isRecording}
              className="bg-gradient-to-r from-[#0460A9] to-[#0350a1] text-white p-2.5 rounded-xl hover:shadow-lg hover:shadow-blue-500/30 disabled:opacity-40 disabled:hover:shadow-none transition-all duration-200 font-semibold active:scale-95"
              aria-label="Send message"
            >
              <Send size={20} />
            </button>
          </form>
          <p className="text-center text-xs text-gray-400 mt-3 font-medium">
            Powered by AI • Always learning
          </p>
        </div>
      </div>
    </div>
  );
}
