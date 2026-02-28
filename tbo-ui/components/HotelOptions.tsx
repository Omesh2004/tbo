'use client';

import React from 'react';
import { Star, Check } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { HotelOption } from '@/lib/types';

interface HotelOptionsProps {
  title?: string;
  hotels: HotelOption[];
  onSelectHotel?: (hotelId: string) => void;
  selectedHotelId?: string;
  compact?: boolean;
  gridCols?: string;
}

export default function HotelOptions({
  title = 'Top Hotel Options',
  hotels,
  onSelectHotel,
  selectedHotelId,
  compact = false,
  gridCols = 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
}: HotelOptionsProps) {
  return (
    <div className={compact ? 'space-y-2' : 'space-y-4'}>
      <h2 className={`${compact ? 'text-lg' : 'text-2xl'} font-bold text-gray-900`}>{title}</h2>

      <div className={`grid ${gridCols} gap-4`}>
        {hotels.map((hotel) => (
          <div
            key={hotel.id}
            onClick={() => onSelectHotel?.(hotel.id)}
            className={`rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-all cursor-pointer border-2 ${
              selectedHotelId === hotel.id
                ? 'border-blue-500 ring-2 ring-blue-200'
                : 'border-transparent hover:border-gray-200'
            }`}
          >
            {/* Image */}
            <div className={`relative ${compact ? 'h-32' : 'h-48'} bg-gray-200 overflow-hidden`}>
              <img
                src={hotel.image}
                alt={hotel.name}
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
              />
              {selectedHotelId === hotel.id && (
                <div className="absolute top-2 right-2 bg-blue-500 text-white p-2 rounded-full">
                  <Check size={16} />
                </div>
              )}
            </div>

            {/* Content */}
            <div className={compact ? 'p-2 space-y-2' : 'p-4 space-y-3'}>
              {/* Name */}
              <h3 className={`font-semibold text-gray-900 ${compact ? 'text-sm' : 'text-base'} leading-tight`}>
                {hotel.name}
              </h3>

              {/* Rating */}
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      size={compact ? 12 : 14}
                      className={`${
                        i < Math.floor(hotel.rating)
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className={`text-gray-600 ${compact ? 'text-xs' : 'text-sm'}`}>
                  {hotel.rating}
                </span>
                <span className={`text-gray-500 ${compact ? 'text-xs' : 'text-sm'}`}>
                  ({hotel.reviewCount.toLocaleString()} Rev)
                </span>
              </div>

              {!compact && (
                <>
                  {/* Amenities */}
                  <div className="flex flex-wrap gap-1">
                    {hotel.amenities.slice(0, 2).map((amenity, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {amenity}
                      </Badge>
                    ))}
                  </div>

                  {/* Cancellation */}
                  {hotel.cancellation && (
                    <div className="flex items-center gap-2 text-green-600 text-sm">
                      <Check size={16} />
                      <span>Free Cancellation</span>
                    </div>
                  )}
                </>
              )}

              {/* Tier Badge and Price */}
              <div className={`flex items-center justify-between ${!compact && 'pt-2 border-t border-gray-200'}`}>
                <Badge
                  variant="outline"
                  className={`text-xs font-semibold ${
                    hotel.tier === 'premium'
                      ? 'bg-blue-100 text-blue-700 border-blue-300'
                      : hotel.tier === 'standard'
                      ? 'bg-orange-100 text-orange-700 border-orange-300'
                      : 'bg-green-100 text-green-700 border-green-300'
                  }`}
                >
                  {hotel.tier.charAt(0).toUpperCase() + hotel.tier.slice(1)}
                </Badge>
                <span className={`font-bold text-gray-900 ${compact ? 'text-base' : 'text-lg'}`}>
                  ${hotel.price}
                  <span className="text-xs text-gray-600 font-normal">{hotel.priceUnit}</span>
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
