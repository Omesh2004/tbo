'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { MapPin, Calendar, Users, Plane } from 'lucide-react';

export interface TravelPlanDetails {
  destination: string;
  fromCity: string;
  startDate: string;
  numberOfDays: number;
  travelers: number;
}

interface TravelPlanFormProps {
  initialDestination?: string;
  onSubmit: (details: TravelPlanDetails) => void;
  disabled?: boolean;
}

const defaultStartDate = () => {
  const d = new Date();
  d.setDate(d.getDate() + 7);
  return d.toISOString().slice(0, 10);
};

export default function TravelPlanForm({
  initialDestination = '',
  onSubmit,
  disabled = false,
}: TravelPlanFormProps) {
  const [destination, setDestination] = useState(initialDestination);
  const [fromCity, setFromCity] = useState('');
  const [startDate, setStartDate] = useState(defaultStartDate());
  const [numberOfDays, setNumberOfDays] = useState(4);
  const [travelers, setTravelers] = useState(2);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!destination.trim() || !fromCity.trim()) return;
    onSubmit({
      destination: destination.trim(),
      fromCity: fromCity.trim(),
      startDate,
      numberOfDays,
      travelers,
    });
  };

  return (
    <div className="flex justify-start">
      <div className="w-full max-w-md pl-[52px]">
        <form
          onSubmit={handleSubmit}
          className="bg-gradient-to-b from-orange-50/50 to-white border border-orange-200/60 rounded-xl p-5 shadow-sm space-y-4"
        >
          <p className="text-sm font-semibold text-gray-800 mb-3">Share a few details so I can create your plan:</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                <MapPin className="inline w-3.5 h-3.5 mr-1" /> Destination
              </label>
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="e.g. Singapore, Paris"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                <Plane className="inline w-3.5 h-3.5 mr-1" /> Travel from (city)
              </label>
              <input
                type="text"
                value={fromCity}
                onChange={(e) => setFromCity(e.target.value)}
                placeholder="e.g. Mumbai, London"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                <Calendar className="inline w-3.5 h-3.5 mr-1" /> Start date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Number of days</label>
              <input
                type="number"
                min={1}
                max={30}
                value={numberOfDays}
                onChange={(e) => setNumberOfDays(parseInt(e.target.value, 10) || 1)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">
                <Users className="inline w-3.5 h-3.5 mr-1" /> Number of travelers
              </label>
              <input
                type="number"
                min={1}
                max={20}
                value={travelers}
                onChange={(e) => setTravelers(parseInt(e.target.value, 10) || 1)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none max-w-[120px]"
              />
            </div>
          </div>
          <Button
            type="submit"
            disabled={disabled || !destination.trim() || !fromCity.trim()}
            className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2.5 rounded-lg"
          >
            Get my plan
          </Button>
        </form>
      </div>
    </div>
  );
}
