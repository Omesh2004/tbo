'use client';

import React, { useState } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import ChatArea from '@/components/ChatArea';
import QuotePanel from '@/components/QuotePanel';
import {
  mockAgent,
  mockChatMessages,
  mockHotels,
  mockTransport,
  mockQuote,
  mockHistory,
  mockSavedPlans,
  mockReports,
  mockRecommendedHotels,
} from '@/lib/mockData';
import { ChatMessage } from '@/lib/types';

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages);
  const [selectedHotel, setSelectedHotel] = useState<string | undefined>();
  const [selectedTransport, setSelectedTransport] = useState<string | undefined>();

  const handleSendMessage = (message: string) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      message,
    };
    setMessages([...messages, newMessage]);

    // Simulate agent response after a delay
    setTimeout(() => {
      const agentMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        avatar: mockAgent.image,
        name: mockAgent.name,
        message: 'I will help you with that. Let me find the best options for you.',
      };
      setMessages((prev) => [...prev, agentMessage]);
    }, 500);
  };

  const handleGeneratePDF = () => {
    alert('PDF generation feature will be implemented');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      {/* Header */}
      <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - Mobile Drawer */}
        {sidebarOpen && (
          <div className="fixed inset-0 z-30 md:hidden bg-black/50" onClick={() => setSidebarOpen(false)}>
            <div onClick={(e) => e.stopPropagation()} className="h-full overflow-auto">
              <Sidebar
                history={mockHistory}
                savedPlans={mockSavedPlans}
                reports={mockReports}
                agent={mockAgent}
                isOpen={sidebarOpen}
              />
            </div>
          </div>
        )}

        {/* Sidebar - Desktop */}
        <Sidebar
          history={mockHistory}
          savedPlans={mockSavedPlans}
          reports={mockReports}
          agent={mockAgent}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col lg:flex-row gap-4 overflow-hidden p-4 bg-white">
          {/* Center: Chat Area */}
          <div className="flex-1 flex flex-col overflow-hidden min-w-0">
            <div className="flex-1 bg-white rounded-lg shadow flex flex-col overflow-hidden">
              <ChatArea
                messages={messages}
                onSendMessage={handleSendMessage}
                hotels={mockHotels}
                selectedHotelId={selectedHotel}
                onSelectHotel={setSelectedHotel}
                transportOptions={mockTransport}
                selectedTransportId={selectedTransport}
                onSelectTransport={setSelectedTransport}
              />
            </div>
          </div>

          {/* Right: Quote Panel */}
          <div className="w-full lg:w-72 flex-shrink-0 overflow-y-auto">
            <QuotePanel
              quote={mockQuote}
              recommendedHotels={mockRecommendedHotels}
              onGeneratePDF={handleGeneratePDF}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
