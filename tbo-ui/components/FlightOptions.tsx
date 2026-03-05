'use client';

import React from 'react';
import { Plane, Clock, Check } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { FlightOption } from '@/lib/types';

// Airline brand gradient map
const AIRLINE_GRADIENTS: Record<string, string> = {
  '6E': 'from-indigo-600 to-indigo-700',   // IndiGo
  'SG': 'from-red-600 to-red-700',          // SpiceJet
  'AI': 'from-orange-700 to-red-700',       // Air India
  'UK': 'from-purple-600 to-purple-700',    // Vistara
  'QP': 'from-orange-500 to-orange-600',    // Akasa Air
  'IX': 'from-red-800 to-red-900',          // Air India Express
  // Gulf / Middle East
  'EK': 'from-red-700 to-red-800',          // Emirates
  'QR': 'from-purple-800 to-purple-900',    // Qatar Airways
  'EY': 'from-gray-700 to-gray-900',        // Etihad
  'FZ': 'from-red-500 to-rose-600',         // flydubai
  'WY': 'from-teal-600 to-teal-700',        // Oman Air
  'GF': 'from-amber-700 to-amber-800',      // Gulf Air
  'KU': 'from-blue-700 to-blue-800',        // Kuwait Airways
  'SV': 'from-green-700 to-green-800',      // Saudia
  'UL': 'from-blue-600 to-cyan-700',        // SriLankan Airlines
  // Southeast Asian
  'SQ': 'from-yellow-600 to-amber-700',     // Singapore Airlines
  'MH': 'from-red-700 to-red-900',          // Malaysia Airlines
  'AK': 'from-red-600 to-red-700',          // AirAsia
  'TG': 'from-purple-600 to-rose-600',      // Thai Airways
  'GA': 'from-blue-700 to-indigo-700',      // Garuda
  'CX': 'from-gray-700 to-gray-800',        // Cathay Pacific
  'NH': 'from-blue-600 to-blue-700',        // ANA
  'JL': 'from-red-700 to-red-800',          // JAL
  // European
  'LH': 'from-yellow-500 to-yellow-600',    // Lufthansa
  'BA': 'from-blue-800 to-blue-900',        // British Airways
  'AF': 'from-blue-600 to-blue-700',        // Air France
  'TK': 'from-rose-600 to-rose-700',        // Turkish Airlines
  'KL': 'from-blue-500 to-blue-600',        // KLM
  // Others
  'ET': 'from-green-600 to-green-700',      // Ethiopian
  'AC': 'from-red-600 to-red-700',          // Air Canada
};

const getGradient = (code?: string) =>
  AIRLINE_GRADIENTS[code || ''] || 'from-blue-600 to-blue-700';

const formatTime = (dt?: string) => {
  if (!dt) return '--:--';
  try {
    return new Date(dt).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return dt.split('T')[1]?.slice(0, 5) || dt;
  }
};

const formatDate = (dt?: string) => {
  if (!dt) return '';
  try {
    return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return dt.split('T')[0] || '';
  }
};

const currencySymbol = (c?: string) => {
  if (c === 'INR') return '₹';
  if (c === 'EUR') return '€';
  if (c === 'GBP') return '£';
  return '$';
};

interface FlightOptionsProps {
  title?: string;
  flights: FlightOption[];
  onSelectFlight?: (flightId: string) => void;
  selectedFlightId?: string;
  compact?: boolean;
}

export default function FlightOptions({
  title = 'Available Flights',
  flights,
  onSelectFlight,
  selectedFlightId,
  compact = false,
}: FlightOptionsProps) {
  return (
    <div className={compact ? 'space-y-2' : 'space-y-4'}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-sm">
          <Plane size={13} className="text-white" />
        </div>
        <h2 className={`${compact ? 'text-lg' : 'text-2xl'} font-bold text-gray-900`}>
          {title}
        </h2>
      </div>

      {/* Flight Cards */}
      <div className="flex flex-col gap-3">
        {flights.map((flight) => {
          const isSelected = selectedFlightId === flight.id;
          return (
            <div
              key={flight.id}
              onClick={() => onSelectFlight?.(flight.id)}
              className={`rounded-xl border-2 cursor-pointer transition-all overflow-hidden shadow-sm hover:shadow-md ${
                isSelected
                  ? 'border-blue-500 ring-2 ring-blue-200'
                  : 'border-transparent hover:border-gray-200'
              }`}
            >
              {/* Airline Header Strip */}
              <div
                className={`bg-gradient-to-r ${getGradient(flight.airlineCode)} px-4 py-2.5 flex items-center justify-between`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <Plane size={14} className="text-white/90 flex-shrink-0" />
                  <span className="text-white font-bold text-sm tracking-wide truncate">
                    {flight.airline}
                  </span>
                  {flight.flightNumber && (
                    <span className="text-white/60 text-xs font-mono flex-shrink-0">
                      {flight.flightNumber}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {isSelected && (
                    <div className="bg-white rounded-full p-0.5 shadow">
                      <Check size={12} className="text-blue-600" />
                    </div>
                  )}
                  <Badge className="bg-white/20 border-white/30 text-white text-xs hover:bg-white/20 border">
                    {flight.cabinClass || 'Economy'}
                  </Badge>
                </div>
              </div>

              {/* Route Body */}
              <div className="bg-white px-4 py-4">
                <div className="flex items-center gap-2">
                  {/* Departure */}
                  <div className="text-center w-[88px] flex-shrink-0">
                    <p className="text-xl font-bold text-gray-900 tabular-nums leading-tight">
                      {formatTime(flight.departureTime)}
                    </p>
                    <p className="text-xs font-semibold text-gray-700 uppercase tracking-wider mt-0.5">
                      {flight.origin}
                    </p>
                    {flight.departureTime && (
                      <p className="text-xs text-gray-400 mt-0.5">
                        {formatDate(flight.departureTime)}
                      </p>
                    )}
                  </div>

                  {/* Connector */}
                  <div className="flex-1 flex flex-col items-center gap-1 min-w-0 px-1">
                    <span className="text-xs text-gray-500 font-medium flex items-center gap-1">
                      <Clock size={10} />
                      {flight.duration}
                    </span>
                    <div className="relative w-full flex items-center">
                      <div className="h-px bg-gray-300 flex-1" />
                      <div className="mx-1 w-5 h-5 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center flex-shrink-0 shadow-sm">
                        <Plane size={9} className="text-blue-500" />
                      </div>
                      <div className="h-px bg-gray-300 flex-1" />
                    </div>
                    <span
                      className={`text-xs font-semibold ${
                        flight.stops === 0 ? 'text-green-600' : 'text-orange-500'
                      }`}
                    >
                      {flight.stops === 0
                        ? 'Nonstop'
                        : flight.stops === 1
                        ? '1 Stop'
                        : `${flight.stops} Stops`}
                    </span>
                  </div>

                  {/* Arrival */}
                  <div className="text-center w-[88px] flex-shrink-0">
                    <p className="text-xl font-bold text-gray-900 tabular-nums leading-tight">
                      {formatTime(flight.arrivalTime)}
                    </p>
                    <p className="text-xs font-semibold text-gray-700 uppercase tracking-wider mt-0.5">
                      {flight.destination}
                    </p>
                    {flight.arrivalTime && (
                      <p className="text-xs text-gray-400 mt-0.5">
                        {formatDate(flight.arrivalTime)}
                      </p>
                    )}
                  </div>

                  {/* Price — hidden on very small screens */}
                  <div className="hidden sm:flex flex-col items-end ml-3 flex-shrink-0 pl-3 border-l border-gray-100">
                    <p className="text-xl font-bold text-gray-900">
                      {currencySymbol(flight.currency)}
                      {flight.price.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-400">per person</p>
                    {isSelected && (
                      <span className="mt-1.5 text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                        ✓ Selected
                      </span>
                    )}
                  </div>
                </div>

                {/* Mobile price row */}
                <div className="mt-2.5 flex items-center justify-between sm:hidden pt-2 border-t border-gray-100">
                  <span className="text-xs text-gray-500">Per person</span>
                  <span className="text-lg font-bold text-gray-900">
                    {currencySymbol(flight.currency)}
                    {flight.price.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
