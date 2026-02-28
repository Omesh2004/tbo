'use client';

import React from 'react';
import { Send, Paperclip } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatMessage, HotelOption, TransportOption } from '@/lib/types';
import HotelOptions from './HotelOptions';
import TransportOptions from './TransportOptions';

interface ChatAreaProps {
  messages: ChatMessage[];
  onSendMessage?: (message: string) => void;
  placeholder?: string;
  hotels?: HotelOption[];
  selectedHotelId?: string;
  onSelectHotel?: (hotelId: string) => void;
  transportOptions?: TransportOption[];
  selectedTransportId?: string;
  onSelectTransport?: (transportId: string) => void;
}

export default function ChatArea({
  messages,
  onSendMessage,
  placeholder = "What would you like to explore next?",
  hotels,
  selectedHotelId,
  onSelectHotel,
  transportOptions,
  selectedTransportId,
  onSelectTransport,
}: ChatAreaProps) {
  const [input, setInput] = React.useState('');
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage?.(input);
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-6 bg-white scrollbar-hidden">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.sender === 'agent' && message.avatar && (
              <img
                src={message.avatar}
                alt={message.name}
                className="w-10 h-10 rounded-full object-cover shrink-0"
              />
            )}
            <div
              className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-2xl ${message.sender === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : 'bg-white text-gray-900 border border-gray-200 rounded-bl-none'
                }`}
            >
              <p className="text-sm leading-relaxed">{message.message}</p>
            </div>
          </div>
        ))}

        {/* Hotel Options in Chat */}
        {hotels && hotels.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="bg-white rounded-lg p-4 lg:p-6">
              <HotelOptions
                title="Top Hotel Options"
                hotels={hotels}
                selectedHotelId={selectedHotelId}
                onSelectHotel={onSelectHotel}
                gridCols="grid-cols-1 sm:grid-cols-2"
              />
            </div>
          </div>
        )}

        {/* Transport Options in Chat */}
        {transportOptions && transportOptions.length > 0 && (
          <div className="mt-4">
            <div className="bg-white rounded-lg p-4 lg:p-6">
              <TransportOptions
                title="Best Transport Options"
                options={transportOptions}
                selectedTransportId={selectedTransportId}
                onSelectTransport={onSelectTransport}
              />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4 lg:p-6">
        <div className="flex gap-2 items-center">
          <div className="flex-1 flex items-center bg-gray-100 rounded-full px-4 py-2 gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder={placeholder}
              className="flex-1 bg-transparent outline-none text-sm text-gray-900 placeholder-gray-600"
            />
            <button className="p-2 hover:bg-gray-200 rounded-full transition-colors">
              <Paperclip size={18} className="text-gray-600" />
            </button>
          </div>
          <Button
            onClick={handleSend}
            className="bg-orange-500 hover:bg-orange-600 text-white rounded-full p-3 h-full flex items-center justify-center transition-colors"
          >
            <Send size={18} />
          </Button>
        </div>
      </div>
    </div>
  );
}
