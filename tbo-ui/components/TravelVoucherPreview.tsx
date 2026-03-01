'use client';

import React, { useRef, useMemo, useId } from 'react';
import { QuoteSummary, HotelOption, TransportOption, Agent } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Printer, X } from 'lucide-react';

function WaveDivider({ id }: { id: string }) {
  return (
    <svg viewBox="0 0 1200 40" className="w-full h-10 flex-shrink-0" preserveAspectRatio="none">
      <path
        fill={`url(#${id})`}
        d="M0 20 Q300 0 600 20 T1200 20 V40 H0 Z"
      />
      <defs>
        <linearGradient id={id} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#2563eb" />
          <stop offset="100%" stopColor="#f97316" />
        </linearGradient>
      </defs>
    </svg>
  );
}

const DEFAULT_ITINERARY = [
  'Day 1: Arrival & Hotel Check-in',
  'Day 2: Sentosa Island Tour',
  'Day 3: Universal Studios Visit',
  'Day 4: Marina Bay & Gardens by the Bay',
  'Day 5: Departure',
];

const DEFAULT_FLIGHTS = {
  departure: { route: 'Mumbai (BOM) → Singapore (SIN)', flight: 'AI 460', date: '05 Dec 2024', time: '10:05 PM', class: 'Economy' },
  return: { route: 'Singapore (SIN) → Mumbai (BOM)', date: '09 Dec 2024', time: '11:30 PM' },
};

const CLIENT_NAME = 'John Doe & Guest';
const TRAVEL_DATES = '05 Dec 2024 – 09 Dec 2024';
const SUPPORT_NUMBER = '+1 987-654-3210';

interface TravelVoucherPreviewProps {
  quote: QuoteSummary;
  selectedHotel?: HotelOption | null;
  selectedTransport?: TransportOption | null;
  agent: Agent;
  bookingRef?: string;
  onClose?: () => void;
  onPrint?: () => void;
  showActions?: boolean;
}

export default function TravelVoucherPreview({
  quote,
  selectedHotel,
  selectedTransport,
  agent,
  bookingRef: bookingRefProp,
  onClose,
  onPrint,
  showActions = true,
}: TravelVoucherPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bookingRef = useMemo(() => bookingRefProp || 'PNR' + Math.random().toString().slice(2, 9), [bookingRefProp]);
  const waveId1 = useId();
  const waveId2 = useId();
  const nights = 4;
  const totalCost = quote.maxPrice || quote.minPrice || 0;
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=${encodeURIComponent(bookingRef)}`;

  const handlePrint = () => {
    if (onPrint) {
      onPrint();
      return;
    }
    // Clone the preview and print only that so output matches what user sees
    const el = containerRef.current;
    if (!el) {
      window.print();
      return;
    }
    const clone = el.cloneNode(true) as HTMLElement;
    clone.querySelectorAll('.no-print, [class*="print:hidden"]').forEach((n) => n.remove());
    clone.id = 'voucher-print-target';
    // Keep voucher at 210mm width when printing: outer scrollable, inner fixed width
    clone.style.cssText =
      'position:fixed !important; inset:0 !important; left:0 !important; top:0 !important; right:0 !important; bottom:0 !important; width:100% !important; height:100% !important; background:#fff !important; z-index:999999 !important; overflow:auto !important; padding:0.5in !important; margin:0 !important; box-sizing:border-box !important;';
    const inner = clone.querySelector('.voucher-inner') as HTMLElement;
    if (inner) {
      inner.style.width = '210mm';
      inner.style.minWidth = '210mm';
      inner.style.maxWidth = '210mm';
      inner.style.marginLeft = 'auto';
      inner.style.marginRight = 'auto';
    }
    document.body.appendChild(clone);
    const cleanup = () => {
      document.getElementById('voucher-print-target')?.remove();
      window.onafterprint = null;
    };
    window.onafterprint = cleanup;
    window.print();
    // Fallback cleanup if afterprint doesn't fire (e.g. cancel)
    setTimeout(cleanup, 1000);
  };

  return (
    <div ref={containerRef} className="voucher-print-container bg-white shrink-0" style={{ minWidth: '210mm', width: '210mm', maxWidth: '100%', margin: '0 auto', boxSizing: 'border-box' }}>
      <title className="hidden print:block">Travel Voucher - {quote.destination}</title>

      <div className="voucher-inner bg-white text-gray-900" style={{ width: '210mm', minWidth: '210mm', maxWidth: '100%', marginLeft: 'auto', marginRight: 'auto', boxSizing: 'border-box' }}>
        <div className="flex items-start justify-between border-b border-gray-200 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-600 to-orange-500 flex items-center justify-center">
              <span className="text-white font-bold text-sm">TBO</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-800">Travel Voucher</h1>
          </div>
          <div className="text-right flex flex-col items-end gap-1">
            <img src={qrUrl} alt="Booking QR" className="w-16 h-16 border border-gray-200 rounded" />
            <span className="text-xs font-medium text-gray-600">Booking Reference: {bookingRef}</span>
          </div>
        </div>

        <WaveDivider id={waveId1} />

        <div className="mt-6 flex flex-wrap gap-6">
          <div className="flex-1 min-w-[280px]">
            <h2 className="text-xl font-bold text-gray-900 mb-1">
              {nights} Nights in {quote.destination} ({quote.date})
            </h2>
            <p className="text-gray-600 text-sm mb-4">Including hotel, flights, and activities.</p>
            <div className="flex items-center justify-between gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div>
                <p className="text-sm font-medium text-gray-700">Total package cost:</p>
                <p className="text-xs text-gray-500 mt-0.5">This trip includes taxes and passes.</p>
              </div>
              <div className="bg-orange-500 text-white px-4 py-2 rounded font-bold text-xl">
                {quote.currency}{totalCost.toLocaleString()}
              </div>
            </div>
            <div className="mt-4 space-y-1 text-sm text-gray-700">
              <p><span className="font-medium">Client:</span> {CLIENT_NAME}</p>
              <p><span className="font-medium">Travel Dates:</span> {TRAVEL_DATES}</p>
              <p><span className="font-medium">Total Package Cost:</span> {quote.currency}{totalCost.toLocaleString()}</p>
            </div>
          </div>
          <div className="w-72 shrink-0 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-3">Travel Summary & Booking Confirmation</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>Booking Reference: {bookingRef}</li>
              <li>Client Name: {CLIENT_NAME}</li>
              <li>Destination: {quote.destination}</li>
              <li>Travel Dates: {TRAVEL_DATES}</li>
              <li className="font-semibold">Total Package Cost: {quote.currency}{totalCost.toLocaleString()}</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 p-4 bg-gray-100 rounded-lg border border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-3">Confirmed Hotel Details</h3>
          {selectedHotel ? (
            <div className="space-y-2 text-sm">
              <p><span className="font-medium">Hotel:</span> {selectedHotel.name} - {selectedHotel.tier && selectedHotel.tier.charAt(0).toUpperCase() + selectedHotel.tier.slice(1)} Room</p>
              <p><span className="font-medium">Address:</span> {quote.destination} (confirm at booking)</p>
              <p><span className="font-medium">Check-in:</span> 05 Dec 2024 | 3:00 PM</p>
              <p><span className="font-medium">Check-out:</span> 09 Dec 2024 | 11:00 AM</p>
              <p>Booking Status: <span className="text-green-600 font-medium">Confirmed</span></p>
              <p>Cancellation Policy: Free cancellation 48 hours prior.</p>
            </div>
          ) : (
            <p className="text-gray-600 text-sm">Select a hotel in the chat to see details here.</p>
          )}
        </div>

        <div className="my-6">
          <WaveDivider id={waveId2} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-3">Travel Summary & Booking Confirmation</h3>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm text-gray-700">
              <span>Booking Reference:</span><span>{bookingRef}</span>
              <span>Client Name:</span><span>{CLIENT_NAME}</span>
              <span>Destination:</span><span>{quote.destination}</span>
              <span>Travel Dates:</span><span>{TRAVEL_DATES}</span>
            </div>
            <div className="mt-3 flex justify-end">
              <span className="bg-orange-500 text-white px-3 py-1 rounded font-bold">{quote.currency}{totalCost.toLocaleString()}</span>
            </div>
          </div>
          <div className="lg:col-span-2 p-4 border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">Flight Details</h3>
            <div className="flex flex-wrap gap-6">
              <div className="space-y-3 text-sm">
                <div>
                  <p className="font-medium text-gray-900">Departure Flight</p>
                  <p>{DEFAULT_FLIGHTS.departure.route}</p>
                  <p>Flight: {DEFAULT_FLIGHTS.departure.flight} {DEFAULT_FLIGHTS.departure.date} | {DEFAULT_FLIGHTS.departure.time}</p>
                  <p>Class: {DEFAULT_FLIGHTS.departure.class}</p>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Return Flight</p>
                  <p>{DEFAULT_FLIGHTS.return.route}</p>
                  <p>Date & Time: {DEFAULT_FLIGHTS.return.date} | {DEFAULT_FLIGHTS.return.time}</p>
                </div>
              </div>
              <div className="ml-auto hidden sm:block">
                <img
                  src={selectedHotel?.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=300&fit=crop'}
                  alt={quote.destination}
                  className="w-32 h-24 object-cover rounded border border-gray-200"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-3">Day-by-Day Itinerary Overview</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            {DEFAULT_ITINERARY.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="mt-6 p-4 bg-gray-100 rounded-lg border border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-3">Emergency & Support Information</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium text-gray-900">Travel Agent Contact</p>
              <p>{agent.name} / {agent.title}</p>
              <p>+1 123-456-7890</p>
            </div>
            <div>
              <p className="font-medium text-gray-900">24/7 Support Number</p>
              <p>{SUPPORT_NUMBER}</p>
            </div>
          </div>
        </div>
      </div>

      {showActions && (
        <div className="flex gap-3 mt-6 print:hidden no-print">
          <Button
            onClick={handlePrint}
            className="bg-orange-500 hover:bg-orange-600 text-white flex items-center gap-2"
          >
            <Printer size={18} />
            Print / Save as PDF
          </Button>
          {onClose && (
            <Button variant="outline" onClick={onClose}>
              <X size={18} className="mr-2" />
              Close
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
