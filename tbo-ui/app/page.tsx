'use client';

import React, { useState, useRef, useEffect, useMemo } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import ChatArea from '@/components/ChatArea';
import TravelVoucherPreview from '@/components/TravelVoucherPreview';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  mockAgent,
  mockHotels,
  mockTransport,
  mockQuote,
  mockHistory,
  mockSavedPlans,
  mockReports,
  mockRecommendedHotels,
} from '@/lib/mockData';
import { ChatMessage, HotelOption, QuoteSummary, TransportOption } from '@/lib/types';
import type { TravelPlanDetails } from '@/components/TravelPlanForm';

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedHotel, setSelectedHotel] = useState<string | undefined>();
  const [selectedTransport, setSelectedTransport] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [travelPlanResponseMessageId, setTravelPlanResponseMessageId] = useState<string | null>(null);
  const [showVoucherPreview, setShowVoucherPreview] = useState(false);
  const [voucherQuote, setVoucherQuote] = useState<QuoteSummary>(mockQuote);
  const [voucherHotel, setVoucherHotel] = useState<HotelOption | null>(null);
  const [voucherTransport, setVoucherTransport] = useState<typeof mockTransport[0] | null>(null);
  const [showTravelPlanForm, setShowTravelPlanForm] = useState(false);
  const [travelPlanFormDestination, setTravelPlanFormDestination] = useState('');
  const [dynamicHotels, setDynamicHotels] = useState<HotelOption[]>(mockHotels);
  const [dynamicTransport, setDynamicTransport] = useState<TransportOption[]>(mockTransport);
  const [travelPlanDetails, setTravelPlanDetails] = useState<TravelPlanDetails | null>(null);

  const displayQuote = useMemo((): QuoteSummary => {
    const details = travelPlanDetails;
    const nights = details?.numberOfDays ?? 4;
    const dest = details?.destination ?? mockQuote.destination;
    const dateStr = details?.startDate
      ? `${new Date(details.startDate).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} (+${nights} days)`
      : mockQuote.date;
    const hotel = selectedHotel ? dynamicHotels.find((h) => h.id === selectedHotel) : undefined;
    const transport = selectedTransport ? dynamicTransport.find((t) => t.id === selectedTransport) : undefined;
    const total = (hotel ? hotel.price * nights : 0) + (transport ? transport.price : 0) || mockQuote.minPrice;
    return {
      destination: dest,
      date: dateStr,
      hotelCost: hotel?.price ?? mockQuote.hotelCost,
      hotelCostUnit: hotel ? '/night' : mockQuote.hotelCostUnit,
      transportCost: transport?.price ?? mockQuote.transportCost,
      transportCostUnit: transport?.priceUnit ?? mockQuote.transportCostUnit,
      minPrice: total || mockQuote.minPrice,
      maxPrice: total || mockQuote.maxPrice,
      currency: mockQuote.currency,
    };
  }, [travelPlanDetails, selectedHotel, selectedTransport]);

  const extractDestination = (text: string): string => {
    const lower = text.toLowerCase();
    const toMatch = lower.match(/(?:to|visit|in|for)\s+([a-z][a-z\s]{1,25}?)(?=\s|,|\.|$)/i);
    if (toMatch) return toMatch[1].trim().replace(/\s+/g, ' ');
    const cityMatch = text.match(/\b(Singapore|Paris|London|Dubai|Bali|Tokyo|New York|Mumbai|Delhi|Bangalore)\b/i);
    return cityMatch ? cityMatch[1] : '';
  };

  // Detect if user message indicates they want a travel plan
  const isTravelPlanIntent = (text: string) => {
    const lower = text.toLowerCase();
    const keywords = [
      'travel plan', 'plan my trip', 'plan a trip', 'plan our trip',
      'book a trip', 'book my trip', 'i want a travel plan', 'i need a travel plan',
      'create a travel plan', 'get a travel plan', 'hotels in', 'hotels for',
      'flights to', 'flights for', 'options for', 'looking for hotels',
      'recommend hotels', 'hotel options', 'transport options', 'vacation to',
      'trip to', 'trip for', 'travel to', 'going to', 'visit '
    ];
    return keywords.some(k => lower.includes(k));
  };

  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = 'en-US';
      }
    }
  }, []);

  // ElevenLabs Text-to-Speech function
  const speakResponse = async (text: string) => {
    try {
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error('Audio fetch failed');

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  // Main logic to handle messaging (both text and voice)
  const processMessage = async (
    text: string,
    isVoiceInput: boolean = false,
    planDetails?: TravelPlanDetails
  ) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      message: text.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);

    const userRequestedTravelPlan = isTravelPlanIntent(text);

    // Only show the full "planning" loading state (steps) when user asked for a travel plan
    const activitySequence = [
      '🔍 Analyzing request',
      '🌐 Searching for hotels & flights',
      '💰 Comparing prices',
      '📊 Analyzing patterns',
      '🎯 Generating recommendations',
    ];

    const thinkingMessageId = (Date.now() + 1).toString();
    const thinkingMessage: ChatMessage = {
      id: thinkingMessageId,
      sender: 'agent',
      avatar: mockAgent.image,
      name: mockAgent.name,
      message: '',
      isLoading: true,
      agentActivity: userRequestedTravelPlan ? activitySequence : [],
      currentActivity: userRequestedTravelPlan ? activitySequence[0] : undefined,
    };

    setMessages((prev) => [...prev, thinkingMessage]);
    setIsLoading(true);

    let currentActivityIndex = 0;
    const activityInterval = setInterval(() => {
      if (!userRequestedTravelPlan) return;
      if (currentActivityIndex < activitySequence.length - 1) {
        currentActivityIndex++;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === thinkingMessageId
              ? {
                ...msg,
                currentActivity: activitySequence[currentActivityIndex],
              }
              : msg
          )
        );
      }
    }, 800);

    try {
      let replyText = '';
      if (planDetails) {
        // Use the new plan API which fully utilizes the orchestrator's travel plan logic
        const checkInDate = new Date(planDetails.startDate);
        const checkOutDate = new Date(checkInDate);
        checkOutDate.setDate(checkOutDate.getDate() + planDetails.numberOfDays);

        const response = await fetch('/api/plan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            origin: planDetails.fromCity,
            destination: planDetails.destination,
            check_in: checkInDate.toISOString().split('T')[0],
            check_out: checkOutDate.toISOString().split('T')[0],
            passengers: planDetails.travelers,
            budget: planDetails.budget ? parseFloat(planDetails.budget.replace(/[^0-9.]/g, '')) || undefined : undefined
          }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Failed to generate plan');

        replyText = `${data.analysis}\n\n---\n**Trip Summary:**\n${data.reasoning}\n\n${data.comparison_summary}`;

        if (data.hotel_options && Array.isArray(data.hotel_options)) {
          const freshHotels = data.hotel_options.map((h: any, idx: number) => ({
            id: h.id || `hotel_${idx}`,
            name: h.name,
            image: h.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500&h=400&fit=crop',
            rating: h.rating,
            reviewCount: h.rating_count,
            price: h.price_per_night,
            priceUnit: '/night',
            amenities: h.amenities || [],
            cancellation: true,
            tier: h.tier || (h.rating >= 4.5 ? 'premium' : 'standard')
          }));
          setDynamicHotels(freshHotels);
          if (freshHotels.length > 0) setSelectedHotel(freshHotels[0].id);
        }

        if (data.flight_options && Array.isArray(data.flight_options)) {
          const freshTransport = data.flight_options.map((f: any, idx: number) => ({
            id: f.id || `flight_${idx}`,
            name: f.airline || "Flight",
            icon: '✈️',
            duration: f.duration || "Direct",
            price: f.price,
            priceUnit: 'per person',
            type: 'shuttle'
          }));
          setDynamicTransport(freshTransport);
          if (freshTransport.length > 0) setSelectedTransport(freshTransport[0].id);
        }
      } else {
        // 1. Send text to Gemini API (or your AI endpoint)
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        replyText = data.text;
      }

      clearInterval(activityInterval);

      // 2. Replace thinking message with actual response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === thinkingMessageId
            ? {
              ...msg,
              message: replyText,
              isLoading: false,
              currentActivity: '✅ Complete',
              agentActivity: [],
            }
            : msg
        )
      );

      // Show travel plan results (quote, hotels, transport) only when user asked for a travel plan
      if (userRequestedTravelPlan) {
        setTravelPlanResponseMessageId(thinkingMessageId);
      }

      // 3. ONLY play the ElevenLabs audio if the user used the microphone
      if (isVoiceInput) {
        speakResponse(replyText);
      }
    } catch (error) {
      console.error('Failed to fetch response:', error);
      clearInterval(activityInterval);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === thinkingMessageId
            ? {
              ...msg,
              message: 'Sorry, I encountered an error connecting to the AI.',
              isLoading: false,
              currentActivity: '❌ Error',
              agentActivity: [],
            }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Triggered when user sends a text message
  const handleSendMessage = (message: string) => {
    const text = message.trim();
    if (!text) return;
    // If user is asking for a travel plan, first show the details form instead of calling the API
    if (isTravelPlanIntent(text) && !isLoading) {
      const userMsg: ChatMessage = {
        id: Date.now().toString(),
        sender: 'user',
        message: text,
      };
      setMessages((prev) => [...prev, userMsg]);
      const agentMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        avatar: mockAgent.image,
        name: mockAgent.name,
        message: "I'd love to help plan your trip! Please share a few details below so I can create your itinerary.",
      };
      setMessages((prev) => [...prev, agentMsg]);
      setTravelPlanFormDestination(extractDestination(text));
      setShowTravelPlanForm(true);
      return;
    }
    processMessage(text, false);
  };

  const handleTravelPlanSubmit = (details: TravelPlanDetails) => {
    setShowTravelPlanForm(false);
    setTravelPlanDetails(details);
    const startFormatted = new Date(details.startDate).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    const summary = `Create a travel plan from ${details.fromCity} to ${details.destination}, ${details.numberOfDays} days, starting ${startFormatted}, for ${details.travelers} traveler${details.travelers > 1 ? 's' : ''}.${details.budget ? ` Budget: ${details.budget}.` : ''}`;
    processMessage(summary, false, details);
  };

  // Triggered when user clicks the Microphone
  const handleToggleVoice = () => {
    if (!recognitionRef.current) {
      alert('Voice input isn\'t supported in this browser. Try Chrome or Edge.');
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
        if (e.error !== 'aborted')
          console.error('Speech recognition error:', e.error);
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const handleGeneratePDF = () => {
    const hotel = selectedHotel ? dynamicHotels.find((h) => h.id === selectedHotel) ?? null : null;
    const transport = selectedTransport ? dynamicTransport.find((t) => t.id === selectedTransport) ?? null : null;
    const nights = travelPlanDetails?.numberOfDays ?? 4;
    const hotelCost = hotel ? hotel.price * nights : 0;
    const transportCost = transport ? transport.price : 0;
    const total = hotelCost + transportCost;
    const currency = '$';
    setVoucherQuote({
      destination: travelPlanDetails?.destination ?? mockQuote.destination,
      date: travelPlanDetails?.startDate
        ? `${new Date(travelPlanDetails.startDate).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} (+${nights} days)`
        : mockQuote.date,
      hotelCost: hotel?.price ?? mockQuote.hotelCost,
      hotelCostUnit: hotel ? `/night (${nights} nights)` : mockQuote.hotelCostUnit,
      transportCost: transport?.price ?? mockQuote.transportCost,
      transportCostUnit: transport?.priceUnit ?? mockQuote.transportCostUnit,
      minPrice: total || mockQuote.minPrice,
      maxPrice: total || mockQuote.maxPrice,
      currency,
    });
    setVoucherHotel(hotel);
    setVoucherTransport(transport);
    setShowVoucherPreview(true);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden" data-chat-app>
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
        <div className="flex-1 flex flex-col overflow-hidden p-4 bg-white">
          <div className="flex-1 bg-white rounded-lg shadow flex flex-col overflow-hidden min-w-0">
            <ChatArea
              messages={messages}
              onSendMessage={handleSendMessage}
              onToggleVoice={handleToggleVoice}
              hotels={dynamicHotels}
              selectedHotelId={selectedHotel}
              onSelectHotel={setSelectedHotel}
              transportOptions={dynamicTransport}
              selectedTransportId={selectedTransport}
              onSelectTransport={setSelectedTransport}
              isLoading={isLoading}
              isRecording={isRecording}
              travelPlanResponseMessageId={travelPlanResponseMessageId}
              quote={displayQuote}
              recommendedHotels={mockRecommendedHotels}
              onGeneratePDF={handleGeneratePDF}
              showTravelPlanForm={showTravelPlanForm}
              travelPlanFormDestination={travelPlanFormDestination}
              onTravelPlanSubmit={handleTravelPlanSubmit}
              travelPlanDetails={travelPlanDetails}
            />
          </div>
        </div>
      </div>

      {/* Travel Voucher PDF Preview Dialog */}
      <Dialog open={showVoucherPreview} onOpenChange={setShowVoucherPreview}>
        <DialogContent
          className="!max-w-[96vw] w-full max-h-[90vh] overflow-auto p-0 gap-0 sm:!max-w-[96vw]"
          showCloseButton={true}
        >
          <DialogHeader className="sr-only">
            <DialogTitle>Travel Voucher Preview</DialogTitle>
          </DialogHeader>
          <div className="p-6 flex justify-center" style={{ minWidth: '210mm' }}>
            <div style={{ width: '210mm', flexShrink: 0 }}>
              <TravelVoucherPreview
                quote={voucherQuote}
                selectedHotel={voucherHotel}
                selectedTransport={voucherTransport}
                agent={mockAgent}
                tripDetails={travelPlanDetails}
                onClose={() => setShowVoucherPreview(false)}
                showActions={true}
              />
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
