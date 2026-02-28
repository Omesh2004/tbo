'use client';

import React from 'react';
import { Agent } from '@/lib/types';

interface AgentResponseProps {
  agent: Agent;
  message: string;
  actionText?: string;
  onAction?: () => void;
}

export default function AgentResponse({
  agent,
  message,
  actionText,
  onAction,
}: AgentResponseProps) {
  return (
    <div className="bg-gray-100 rounded-2xl p-4 lg:p-6 space-y-3">
      <div className="flex items-center gap-3">
        <img
          src={agent.image}
          alt={agent.name}
          className="w-12 h-12 rounded-full object-cover"
        />
        <div>
          <h3 className="font-semibold text-gray-900">{agent.name}</h3>
          <p className="text-sm text-gray-600">{agent.title}</p>
        </div>
      </div>
      <p className="text-gray-800 leading-relaxed">{message}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="text-blue-600 hover:text-blue-700 font-medium text-sm transition-colors"
        >
          {actionText} →
        </button>
      )}
    </div>
  );
}
