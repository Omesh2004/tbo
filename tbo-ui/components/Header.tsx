'use client';

import React from 'react';
import { Clock, Star, FileText, ChevronLeft, ChevronRight, Menu, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  logoSrc?: string;
  onMenuClick?: () => void;
  onHistoryClick?: () => void;
  onSavedPlansClick?: () => void;
}

export default function Header({
  logoSrc = 'https://images.unsplash.com/photo-1493514789a586cb23579a9640dc228b5b250312?w=40&h=40&fit=crop',
  onMenuClick,
  onHistoryClick,
  onSavedPlansClick,
}: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-4 lg:px-6 sticky top-0 z-40">
      <div className="flex items-center justify-between">
        {/* Left: Logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Menu size={20} className="text-gray-600" />
          </button>
          <div className="flex items-center gap-2">
            <img src={logoSrc} alt="TBO Logo" className="w-8 h-8 rounded" />
            <span className="font-bold text-xl text-gray-900 hidden sm:inline">tbo</span>
          </div>
        </div>

        {/* Right: Navigation */}
        <div className="flex items-center gap-2 lg:gap-4">
          <button
            onClick={onHistoryClick}
            className="hidden sm:flex items-center gap-2 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors text-sm"
          >
            <Clock size={18} />
            <span className="hidden md:inline">History</span>
          </button>
          <button
            onClick={onSavedPlansClick}
            className="hidden sm:flex items-center gap-2 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors text-sm"
          >
            <Star size={18} className="text-yellow-500" />
            <span className="hidden md:inline">Saved Plans</span>
          </button>
          <button className="hidden sm:flex items-center gap-2 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors text-sm">
            <FileText size={18} />
          </button>
          <Button className="bg-orange-500 hover:bg-orange-600 text-white hidden sm:inline-flex">
            Get Started
          </Button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <MoreVertical size={18} className="text-gray-600" />
          </button>
        </div>
      </div>
    </header>
  );
}
