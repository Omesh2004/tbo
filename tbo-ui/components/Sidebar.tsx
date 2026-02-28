'use client';

import React from 'react';
import { Clock, Star, FileText, MapPin } from 'lucide-react';
import { HistoryItem, SavedPlan, Report, Agent } from '@/lib/types';

interface SidebarProps {
  history: HistoryItem[];
  savedPlans: SavedPlan[];
  reports: Report[];
  agent: Agent;
  isOpen?: boolean;
}

export default function Sidebar({
  history,
  savedPlans,
  reports,
  agent,
  isOpen = true,
}: SidebarProps) {
  const [activeTab, setActiveTab] = React.useState<'history' | 'plans' | 'reports'>('history');

  return (
    <div className={`
      hidden md:flex flex-col flex-shrink-0 w-64 lg:w-72 bg-gradient-to-b from-blue-50 to-white border-r border-gray-200
      ${isOpen ? 'block' : 'hidden'}
      transition-all duration-300 h-full
    `}>
      {/* Agent Profile */}
      <div className="px-4 py-3 border-b border-gray-200 flex-shrink-0">
        <div className="flex flex-col items-center">
          <img
            src={agent.image}
            alt={agent.name}
            className="w-20 h-20 rounded-full object-cover mb-2 border-2 border-blue-500"
          />
          <h3 className="font-semibold text-gray-900 text-center text-sm">{agent.name}</h3>
          <p className="text-xs text-gray-600 text-center">{agent.title}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex justify-around border-b border-gray-200 px-2 flex-shrink-0">
        <button
          onClick={() => setActiveTab('history')}
          className={`flex items-center gap-1 px-2 py-2 text-xs font-medium rounded-t transition-colors ${
            activeTab === 'history'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Clock size={16} />
          <span className="hidden sm:inline">History</span>
        </button>
        <button
          onClick={() => setActiveTab('plans')}
          className={`flex items-center gap-1 px-2 py-2 text-xs font-medium rounded-t transition-colors ${
            activeTab === 'plans'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Star size={16} />
          <span className="hidden sm:inline">Plans</span>
        </button>
        <button
          onClick={() => setActiveTab('reports')}
          className={`flex items-center gap-1 px-2 py-2 text-xs font-medium rounded-t transition-colors ${
            activeTab === 'reports'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <FileText size={16} />
          <span className="hidden sm:inline">Reports</span>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-3 py-4 max-h-fit">
        {activeTab === 'history' && (
          <div className="space-y-1">
            {history.length > 0 ? (
              history.map((item) => (
                <div
                  key={item.id}
                  className="p-2 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors group"
                >
                  <p className="text-xs font-medium text-gray-900 group-hover:text-blue-600">
                    {item.destination}
                  </p>
                  <p className="text-xs text-gray-500">{item.date}</p>
                </div>
              ))
            ) : (
              <p className="text-xs text-gray-500 text-center py-4">No history yet</p>
            )}
          </div>
        )}

        {activeTab === 'plans' && (
          <div className="space-y-1">
            {savedPlans.length > 0 ? (
              savedPlans.map((plan) => (
                <div
                  key={plan.id}
                  className="p-2 rounded-lg hover:bg-yellow-50 cursor-pointer transition-colors group"
                >
                  <div className="flex items-start gap-2">
                    <Star size={14} className="text-yellow-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-900 group-hover:text-blue-600 truncate">
                        {plan.name}
                      </p>
                      <p className="text-xs text-gray-500">{plan.destination}</p>
                      <p className="text-xs font-semibold text-blue-600">{plan.price}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-gray-500 text-center py-4">No saved plans</p>
            )}
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="space-y-1">
            {reports.length > 0 ? (
              reports.map((report) => (
                <div
                  key={report.id}
                  className="p-2 rounded-lg hover:bg-purple-50 cursor-pointer transition-colors group"
                >
                  <div className="flex items-start gap-2">
                    <span className="text-base flex-shrink-0">{report.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-900 group-hover:text-blue-600">
                        {report.title}
                      </p>
                      <p className="text-xs text-gray-500">{report.date}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-gray-500 text-center py-4">No reports</p>
            )}
          </div>
        )}
      </div>

      {/* Map Section */}
      <div className="px-3 py-4 border-t border-gray-200 flex-shrink-0">
        <div className="rounded-lg overflow-hidden h-28 bg-gray-200 flex items-center justify-center">
          <div className="text-center">
            <MapPin size={20} className="text-blue-600 mx-auto mb-1" />
            <p className="text-xs text-gray-600">Singapore</p>
            <p className="text-xs text-gray-600">Changi Airport</p>
          </div>
        </div>
      </div>
    </div>
  );
}
