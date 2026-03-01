// Trip and Travel Data Types
export interface Trip {
  id: string;
  destination: string;
  month: string;
  travelers: string;
  description: string;
  hotelPreference?: string;
  transportPreference?: string;
  budget?: string;
}

export interface HistoryItem {
  id: string;
  date: string;
  destination: string;
  thumbnail?: string;
}

export interface SavedPlan {
  id: string;
  name: string;
  destination: string;
  date: string;
  price: string;
  thumbnail?: string;
}

export interface HotelOption {
  id: string;
  name: string;
  image: string;
  rating: number;
  reviewCount: number;
  price: number;
  priceUnit: string;
  amenities: string[];
  cancellation: boolean;
  tier: 'basic' | 'standard' | 'premium';
}

export interface TransportOption {
  id: string;
  name: string;
  icon?: string;
  duration: string;
  price: number;
  priceUnit?: string;
  description?: string;
  type: 'shuttle' | 'car' | 'train' | 'bus';
}

export interface QuoteSummary {
  destination: string;
  date: string;
  hotelCost: number;
  hotelCostUnit: string;
  transportCost: number;
  transportCostUnit: string;
  minPrice: number;
  maxPrice: number;
  currency: string;
  breakdown?: BreakdownItem[];
}

export interface BreakdownItem {
  label: string;
  value: string;
  type?: 'hotel' | 'transport' | 'activity' | 'other';
}

export interface Agent {
  id: string;
  name: string;
  title: string;
  image: string;
  bio?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  avatar?: string;
  name?: string;
  message: string;
  timestamp?: string;
  isLoading?: boolean;
  agentActivity?: string[];
  currentActivity?: string;
}

export interface Report {
  id: string;
  title: string;
  date: string;
  icon?: string;
  description?: string;
}

export interface RecommendedHotel {
  id: string;
  rank: number;
  name: string;
  nights: number;
  price: number;
  image?: string;
}
