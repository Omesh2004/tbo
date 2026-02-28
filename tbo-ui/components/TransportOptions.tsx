'use client';

import React from 'react';
import { Car, Bus, Radio } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { TransportOption } from '@/lib/types';

interface TransportOptionsProps {
  title?: string;
  options: TransportOption[];
  onSelectTransport?: (transportId: string) => void;
  selectedTransportId?: string;
}

const getTransportIcon = (type: string) => {
  switch (type) {
    case 'shuttle':
      return <Bus size={32} className="text-blue-600" />;
    case 'car':
      return <Car size={32} className="text-blue-600" />;
    case 'train':
      return <Radio size={32} className="text-blue-600" />;
    default:
      return <Bus size={32} className="text-blue-600" />;
  }
};

export default function TransportOptions({
  title = 'Best Transport Options',
  options,
  onSelectTransport,
  selectedTransportId,
}: TransportOptionsProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-900">{title}</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {options.map((option) => (
          <div
            key={option.id}
            onClick={() => onSelectTransport?.(option.id)}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              selectedTransportId === option.id
                ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                : 'border-gray-200 bg-white hover:border-blue-300'
            }`}
          >
            <div className="flex items-start gap-4">
              {/* Icon */}
              <div className="flex-shrink-0">
                {getTransportIcon(option.type)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Name and Duration */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-900 text-lg">
                      {option.name}
                    </h3>
                    <p className="text-sm text-gray-600">{option.duration}</p>
                  </div>
                  <span className="text-lg font-bold text-gray-900 whitespace-nowrap">
                    ${option.price}
                  </span>
                </div>

                {/* Description and Unit */}
                {option.description && (
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">{option.description}</span>
                  </p>
                )}

                {/* Unit Badge */}
                {option.priceUnit && (
                  <Badge variant="secondary" className="text-xs">
                    {option.priceUnit}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
