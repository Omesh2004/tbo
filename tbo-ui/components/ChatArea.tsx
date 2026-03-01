'use client';

import React from 'react';
import { Send, Paperclip, Mic, Square, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChatMessage, HotelOption, TransportOption, QuoteSummary, RecommendedHotel } from '@/lib/types';
import HotelOptions from './HotelOptions';
import TransportOptions from './TransportOptions';
import TravelPlanForm, { TravelPlanDetails } from './TravelPlanForm';

interface ChatAreaProps {
  messages: ChatMessage[];
  onSendMessage?: (message: string) => void;
  onToggleVoice?: () => void;
  placeholder?: string;
  hotels?: HotelOption[];
  selectedHotelId?: string;
  onSelectHotel?: (hotelId: string) => void;
  transportOptions?: TransportOption[];
  selectedTransportId?: string;
  onSelectTransport?: (transportId: string) => void;
  isLoading?: boolean;
  isRecording?: boolean;
  travelPlanResponseMessageId?: string | null;
  quote?: QuoteSummary;
  recommendedHotels?: RecommendedHotel[];
  onGeneratePDF?: () => void;
  showTravelPlanForm?: boolean;
  travelPlanFormDestination?: string;
  onTravelPlanSubmit?: (details: TravelPlanDetails) => void;
}

export default function ChatArea({
  messages,
  onSendMessage,
  onToggleVoice,
  placeholder = "What would you like to explore next?",
  hotels,
  selectedHotelId,
  onSelectHotel,
  transportOptions,
  selectedTransportId,
  onSelectTransport,
  isLoading = false,
  isRecording = false,
  travelPlanResponseMessageId = null,
  quote,
  recommendedHotels = [],
  onGeneratePDF,
  showTravelPlanForm = false,
  travelPlanFormDestination = '',
  onTravelPlanSubmit,
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
      <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-6 bg-white scrollbar-hidden flex flex-col">
        {messages.length === 0 && !isLoading ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center px-4 py-12">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-orange-500 flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-white">TBO</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Your Intelligent Travel Agent</h2>
            <p className="text-gray-500 max-w-sm mb-6">
              Ask for travel plans, hotel options, transport, or anything travel-related. I can help you find and compare options.
            </p>
            <p className="text-sm text-gray-400">Type a message below or use the microphone to get started.</p>
          </div>
        ) : (
          <>
        {messages.map((message) => (
          <React.Fragment key={message.id}>
          <div
            className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.sender === 'agent' && message.avatar && (
              <div className="relative shrink-0">
                {message.isLoading && (
                  <span className="absolute inset-0 rounded-full bg-orange-400/20 animate-ping" style={{ animationDuration: '2s' }} />
                )}
                <img
                  src={message.avatar}
                  alt={message.name}
                  className={`w-10 h-10 rounded-full object-cover relative z-10 ring-2 transition-all ${
                    message.isLoading ? 'ring-orange-200 ring-offset-2' : 'ring-transparent'
                  }`}
                />
              </div>
            )}
            <div
              className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-2xl ${message.sender === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : 'bg-white text-gray-900 border border-gray-200 rounded-bl-none'
                }`}
            >
              {/* Regular message content */}
              {!message.isLoading && (
                <p className="text-sm leading-relaxed">{message.message}</p>
              )}

              {/* Premium Loading State */}
              {message.isLoading && (
                <div className="relative py-1">
                  {/* Typing indicator */}
                  <div className="flex items-center gap-1.5 mb-4">
                    <span className="flex gap-1">
                      <span className="w-2 h-2 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 animate-bounce-dot-1" />
                      <span className="w-2 h-2 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 animate-bounce-dot-2" />
                      <span className="w-2 h-2 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 animate-bounce-dot-3" />
                    </span>
                    <span className="text-xs font-medium text-gray-500 tracking-wide uppercase">Thinking</span>
                  </div>

                  {/* Step progress timeline */}
                  {message.agentActivity && message.agentActivity.length > 0 && (
                    <div className="relative">
                      {message.agentActivity.map((activity, idx) => {
                        const currentIdx = message.agentActivity?.findIndex(a => a === message.currentActivity) ?? -1;
                        const allDone = message.currentActivity === '✅ Complete' || message.currentActivity?.startsWith('❌');
                        const isCompleted = allDone || (currentIdx >= 0 && idx < currentIdx);
                        const isCurrent = !allDone && activity === message.currentActivity;
                        const isLast = idx === (message.agentActivity?.length ?? 1) - 1;

                        return (
                          <div key={idx} className="relative flex">
                            {/* Vertical connector line */}
                            {!isLast && (
                              <div
                                className={`absolute left-3 top-7 w-0.5 h-[calc(100%+8px)] -mb-2 ${
                                  isCompleted ? 'bg-emerald-300' : 'bg-gray-200'
                                }`}
                              />
                            )}
                            <div
                              className={`relative flex items-center gap-3 py-2 px-3 -mx-3 rounded-lg transition-all duration-300 z-10 ${
                                isCurrent
                                  ? 'bg-gradient-to-r from-orange-50/80 to-amber-50/80 ring-1 ring-orange-200/50'
                                  : ''
                              }`}
                            >
                              {/* Step indicator */}
                              <div className="relative flex-shrink-0">
                                {isCurrent ? (
                                  <span className="flex h-6 w-6 items-center justify-center">
                                    <span className="absolute h-6 w-6 rounded-full bg-orange-400/30 animate-ping" style={{ animationDuration: '1.5s' }} />
                                    <span className="relative h-5 w-5 rounded-full border-2 border-orange-500 flex items-center justify-center bg-white shadow-sm">
                                      <span className="h-1.5 w-1.5 rounded-full bg-orange-500 animate-pulse" />
                                    </span>
                                  </span>
                                ) : (
                                  <span
                                    className={`flex h-6 w-6 items-center justify-center rounded-full border-2 transition-all duration-300 ${
                                      isCompleted
                                        ? 'border-emerald-500 bg-emerald-500 shadow-sm'
                                        : 'border-gray-200 bg-white'
                                    }`}
                                  >
                                    {isCompleted ? (
                                      <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                      </svg>
                                    ) : (
                                      <span className="h-1.5 w-1.5 rounded-full bg-gray-300" />
                                    )}
                                  </span>
                                )}
                              </div>
                              <span
                                className={`text-sm transition-all duration-300 ${
                                  isCurrent
                                    ? 'font-semibold text-gray-900'
                                    : isCompleted
                                      ? 'text-gray-600'
                                      : 'text-gray-400'
                                }`}
                              >
                                {activity.replace(/^[^\w\s]+\s*/, '')}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Travel Plan Block - inline in chat, only after user requested travel plan */}
          {message.sender === 'agent' && message.id === travelPlanResponseMessageId && travelPlanResponseMessageId && (
            <div className="flex justify-start">
              <div className="w-full max-w-4xl xl:max-w-5xl pl-[52px] space-y-4">
                {/* Total Quote Summary */}
                {quote && (
                  <div className="bg-white border border-gray-200 rounded-xl p-4 lg:p-5 shadow-sm">
                    <h3 className="text-base font-bold text-gray-900 mb-3">Total Quote</h3>
                    <div className="space-y-2 mb-3">
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">Trip to {quote.destination}:</span> {quote.date}
                      </p>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Hotel Cost</span>
                        <span className="font-semibold text-gray-900">
                          {quote.currency}{quote.hotelCost}{quote.hotelCostUnit}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Transport Cost</span>
                        <span className="font-semibold text-gray-900">
                          {quote.currency}{quote.transportCost}{quote.transportCostUnit}
                        </span>
                      </div>
                    </div>
                    <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 mb-3">
                      <p className="text-lg font-bold text-gray-900">
                        {quote.currency}{quote.minPrice.toLocaleString()} – {quote.currency}{quote.maxPrice.toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">Final price depends on hotel and dates</p>
                    </div>
                    {onGeneratePDF && (
                      <Button
                        onClick={onGeneratePDF}
                        className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2 rounded-lg flex items-center justify-center gap-2 text-sm"
                      >
                        <Download size={16} />
                        Generate PDF
                      </Button>
                    )}
                  </div>
                )}

                {/* Top Hotel Options */}
                {hotels && hotels.length > 0 && (
                  <div className="bg-white rounded-xl p-4 lg:p-5 border border-gray-200 shadow-sm">
                    <HotelOptions
                      title="Top Hotel Options"
                      hotels={hotels}
                      selectedHotelId={selectedHotelId}
                      onSelectHotel={onSelectHotel}
                      gridCols="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
                      compact
                    />
                  </div>
                )}

                {/* Best Transport Options */}
                {transportOptions && transportOptions.length > 0 && (
                  <div className="bg-white rounded-xl p-4 lg:p-5 border border-gray-200 shadow-sm">
                    <TransportOptions
                      title="Best Transport Options"
                      options={transportOptions}
                      selectedTransportId={selectedTransportId}
                      onSelectTransport={onSelectTransport}
                    />
                  </div>
                )}
              </div>
            </div>
          )}
          </React.Fragment>
        ))}

        {/* In-chat form to collect travel details when user asked for a plan */}
        {showTravelPlanForm && onTravelPlanSubmit && (
          <TravelPlanForm
            initialDestination={travelPlanFormDestination}
            onSubmit={onTravelPlanSubmit}
            disabled={isLoading}
          />
        )}

        <div ref={messagesEndRef} />
          </>
        )}

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
              placeholder={isRecording ? 'Listening...' : placeholder}
              disabled={isLoading || isRecording}
              className="flex-1 bg-transparent outline-none text-sm text-gray-900 placeholder-gray-600 disabled:opacity-50"
            />
            <button
              onClick={onToggleVoice}
              disabled={isLoading}
              className={`p-2 rounded-full transition-colors ${
                isRecording
                  ? 'bg-red-500 text-white hover:bg-red-600'
                  : 'hover:bg-gray-200 text-gray-600'
              }`}
              aria-label={isRecording ? 'Stop recording' : 'Start recording'}
            >
              {isRecording ? <Square size={18} fill="currentColor" /> : <Mic size={18} />}
            </button>
            <button className="p-2 hover:bg-gray-200 rounded-full transition-colors">
              <Paperclip size={18} className="text-gray-600" />
            </button>
          </div>
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading || isRecording}
            className="bg-orange-500 hover:bg-orange-600 text-white rounded-full p-3 h-full flex items-center justify-center transition-colors disabled:opacity-50"
          >
            <Send size={18} />
          </Button>
        </div>
      </div>
    </div>
  );
}
