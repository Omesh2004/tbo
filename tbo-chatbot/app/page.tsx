"use client";

import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Loader2, Mic, Square } from "lucide-react"; // Added Mic and Square

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export default function FullPageChat() {
  const [messages, setMessages] = useState<Message[]>([
    { id: "1", role: "assistant", content: "Hello! How can I help you today? Type or click the mic to speak." },
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
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
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
  const processMessage = async (text: string, isVoiceInput: boolean = false) => {
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
      setMessages((prev) => [...prev, { 
        id: Date.now().toString(), 
        role: "assistant", 
        content: "Sorry, I encountered an error connecting to the AI." 
      }]);
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
        if (e.error !== "aborted") console.error("Speech recognition error:", e.error);
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
    <div className="flex flex-col h-screen w-full bg-white">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <h2 className="font-semibold text-slate-800 flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-600" />
            AI Voice Assistant
          </h2>
          {isRecording && (
            <div className="flex items-center gap-2 text-xs font-medium text-red-500 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-red-500"></span>
              Listening...
            </div>
          )}
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto bg-slate-50/50">
        <div className="max-w-3xl mx-auto w-full p-4 space-y-6 pb-8 mt-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start gap-4 ${
                message.role === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-emerald-500 text-white"
                }`}
              >
                {message.role === "user" ? <User size={16} /> : <Bot size={16} />}
              </div>

              <div
                className={`max-w-[85%] text-base leading-relaxed ${
                  message.role === "user"
                    ? "bg-blue-600 text-white px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm"
                    : "text-slate-800 px-5 py-3 bg-white border border-gray-200 rounded-2xl rounded-tl-sm shadow-sm"
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center mt-1">
                <Bot size={16} />
              </div>
              <div className="bg-white border border-gray-200 text-slate-500 text-sm px-5 py-3 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-3xl mx-auto">
          <form
            onSubmit={handleSubmit}
            className={`flex items-center gap-2 bg-slate-50 border rounded-full px-2 py-2 transition-all shadow-sm ${
              isRecording 
                ? "border-red-500 ring-2 ring-red-500/20 bg-red-50/50" 
                : "border-gray-300 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500"
            }`}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isRecording ? "Listening..." : "Message AI Assistant..."}
              disabled={isLoading || isRecording}
              className="flex-1 bg-transparent px-4 py-2 focus:outline-none text-slate-800 disabled:opacity-50 text-base"
            />
            
            {/* Microphone Button */}
            <button
              type="button"
              onClick={toggleVoice}
              disabled={isLoading}
              className={`p-2.5 rounded-full transition-colors disabled:opacity-50 ${
                isRecording 
                  ? "bg-red-500 text-white animate-pulse hover:bg-red-600" 
                  : "text-slate-500 hover:text-slate-800 hover:bg-slate-200/50"
              }`}
            >
              {isRecording ? <Square size={18} fill="currentColor" /> : <Mic size={18} />}
            </button>

            {/* Send Text Button */}
            <button
              type="submit"
              disabled={!input.trim() || isLoading || isRecording}
              className="bg-blue-600 text-white p-2.5 rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
            >
              <Send size={18} />
            </button>
          </form>
          <div className="text-center mt-2">
            <span className="text-xs text-gray-400">AI can make mistakes. Consider verifying important information.</span>
          </div>
        </div>
      </div>

    </div>
  );
}