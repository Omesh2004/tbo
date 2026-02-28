'use client';

import React from 'react';
import { Download, ChevronDown, Eye, Edit3, Share2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { QuoteSummary, RecommendedHotel } from '@/lib/types';

interface QuotePanelProps {
  quote: QuoteSummary;
  recommendedHotels?: RecommendedHotel[];
  onGeneratePDF?: () => void;
  onViewDetails?: () => void;
}

export default function QuotePanel({
  quote,
  recommendedHotels = [],
  onGeneratePDF,
  onViewDetails,
}: QuotePanelProps) {
  const [showBreakdown, setShowBreakdown] = React.useState(false);

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 p-3 lg:p-4">
        <h2 className="text-lg lg:text-xl font-bold text-gray-900">Total Quote</h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 lg:p-4 space-y-4 scrollbar-hidden">
        {/* Trip Summary */}
        <div>
          <h3 className="text-base font-semibold text-gray-900 mb-1">
            Trip to {quote.destination}:
          </h3>
          <p className="text-sm text-gray-600">{quote.date}</p>
        </div>

        {/* Cost Breakdown */}
        <div className="space-y-2">
          <div className="flex justify-between items-center pb-2 border-b border-gray-200">
            <span className="text-sm text-gray-700">Hotel Cost</span>
            <span className="font-semibold text-sm text-gray-900">
              ${quote.hotelCost}
              <span className="text-xs text-gray-600 font-normal"> {quote.hotelCostUnit}</span>
            </span>
          </div>
          <div className="flex justify-between items-center pb-2 border-b border-gray-200">
            <span className="text-sm text-gray-700">Transport Cost</span>
            <span className="font-semibold text-sm text-gray-900">
              ${quote.transportCost}
              <span className="text-xs text-gray-600 font-normal"> {quote.transportCostUnit}</span>
            </span>
          </div>

          {/* Breakdown Toggle */}
          <button
            onClick={() => setShowBreakdown(!showBreakdown)}
            className="flex items-center gap-2 w-full py-1 text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors"
          >
            <span>Breakdown</span>
            <ChevronDown
              size={16}
              className={`transition-transform ${showBreakdown ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Detailed Breakdown */}
          {showBreakdown && quote.breakdown && (
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              {quote.breakdown.map((item, idx) => (
                <div key={idx} className="flex justify-between text-sm">
                  <span className="text-gray-600">{item.label}</span>
                  <span className="font-medium text-gray-900">{item.value}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200" />

        {/* Quote Summary */}
        <div>
          <h3 className="text-base font-semibold text-gray-900 mb-2">Quote Summary</h3>
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 mb-3">
            <p className="text-xl lg:text-2xl font-bold text-gray-900">
              {quote.currency}
              {quote.minPrice.toLocaleString()} – {quote.currency}
              {quote.maxPrice.toLocaleString()}
            </p>
            <p className="text-xs text-gray-600 mt-1">Final price depends on hotel and dates</p>
          </div>
        </div>

        {/* Generate PDF Button */}
        <Button
          onClick={onGeneratePDF}
          className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2 rounded-lg flex items-center justify-center gap-2 text-sm"
        >
          <Download size={16} />
          <span>Generate PDF</span>
        </Button>

        {/* Recommended Hotels */}
        {recommendedHotels.length > 0 && (
          <div>
            <h3 className="text-base font-semibold text-gray-900 mb-2">Your Top Picks</h3>
            <div className="space-y-2">
              {recommendedHotels.map((hotel) => (
                <div
                  key={hotel.id}
                  className="flex gap-2 p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                >
                  {/* Hotel Image */}
                  {hotel.image && (
                    <img
                      src={hotel.image}
                      alt={hotel.name}
                      className="w-10 h-10 rounded object-cover flex-shrink-0"
                    />
                  )}

                  {/* Hotel Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-0.5">
                      <span className="text-xs font-semibold text-gray-900">
                        Rank: {hotel.rank}
                      </span>
                    </div>
                    <p className="text-xs text-gray-700 truncate font-medium">
                      {hotel.name}
                    </p>
                    <p className="text-xs text-gray-600">
                      {hotel.nights} nights, ${hotel.price.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-200">
          <Button
            onClick={onViewDetails}
            variant="outline"
            className="flex items-center justify-center gap-1 py-1 h-auto"
          >
            <Eye size={14} />
            <span className="hidden sm:inline text-xs">View</span>
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-1 py-1 h-auto">
            <Edit3 size={14} />
            <span className="hidden sm:inline text-xs">Edit</span>
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-1 py-1 h-auto">
            <Share2 size={14} />
            <span className="hidden sm:inline text-xs">Share</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
