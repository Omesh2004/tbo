import {
  ChatMessage,
  HotelOption,
  TransportOption,
  QuoteSummary,
  HistoryItem,
  SavedPlan,
  Report,
  RecommendedHotel,
  Agent,
} from './types';

export const mockAgent: Agent = {
  id: '1',
  name: 'John Smith',
  title: 'Travel Agent',
  image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop',
  bio: 'Expert travel consultant with 10+ years of experience',
};

export const mockChatMessages: ChatMessage[] = [
  {
    id: '1',
    sender: 'user',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop',
    name: 'You',
    message: 'I need options for a couple traveling to Singapore in early December. Looking for hotels near the port and transport from airport.',
  },
  {
    id: '2',
    sender: 'agent',
    avatar: mockAgent.image,
    name: mockAgent.name,
    message: 'Sure, here are your best options for Singapore in early December. Let\'s start with some top hotels near the port and transport from the airport.',
  },
];

export const mockHotels: HotelOption[] = [
  {
    id: '1',
    name: 'Marina Bay Sands',
    image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500&h=400&fit=crop',
    rating: 4.5,
    reviewCount: 5432,
    price: 320,
    priceUnit: '/night',
    amenities: ['Free WiFi', 'Pool', 'Gym', 'Spa'],
    cancellation: true,
    tier: 'premium',
  },
  {
    id: '2',
    name: 'The Fullerton Hotel',
    image: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=500&h=400&fit=crop',
    rating: 4.6,
    reviewCount: 3876,
    price: 260,
    priceUnit: '/night',
    amenities: ['Breakfast Included', 'Pool', 'Business Center'],
    cancellation: true,
    tier: 'premium',
  },
  {
    id: '3',
    name: 'Parkroyal Collection',
    image: 'https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=500&h=400&fit=crop',
    rating: 4.5,
    reviewCount: 4190,
    price: 210,
    priceUnit: '/night',
    amenities: ['Rooftop Pool', 'Restaurant', 'Concierge'],
    cancellation: true,
    tier: 'premium',
  },
];

export const mockTransport: TransportOption[] = [
  {
    id: '1',
    name: 'Shared Airport Shuttle',
    icon: '🚐',
    duration: '35-40 min',
    price: 20,
    priceUnit: 'per person',
    type: 'shuttle',
  },
  {
    id: '2',
    name: 'Private Car Transfer',
    icon: '🚗',
    duration: '25-30 min',
    price: 20,
    priceUnit: 'flat rate',
    description: 'Sedan',
    type: 'car',
  },
];

export const mockQuote: QuoteSummary = {
  destination: 'Singapore',
  date: 'Early December',
  hotelCost: 260,
  hotelCostUnit: '/night',
  transportCost: 20,
  transportCostUnit: 'from',
  minPrice: 1120,
  maxPrice: 1280,
  currency: '$',
  breakdown: [
    { label: 'Hotel (4 nights)', value: '$1,040', type: 'hotel' },
    { label: 'Transport', value: '$20-40', type: 'transport' },
    { label: 'Meals & Activities', value: '$60-200', type: 'activity' },
  ],
};

export const mockHistory: HistoryItem[] = [
  { id: '1', date: 'Jan 15, 2024', destination: 'Paris, France', thumbnail: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=200&h=150&fit=crop' },
  { id: '2', date: 'Dec 20, 2023', destination: 'Tokyo, Japan', thumbnail: 'https://images.unsplash.com/photo-1540959375944-7049f642e9f1?w=200&h=150&fit=crop' },
  { id: '3', date: 'Nov 10, 2023', destination: 'Bali, Indonesia', thumbnail: 'https://images.unsplash.com/photo-1537225228614-b120b6daac38?w=200&h=150&fit=crop' },
];

export const mockSavedPlans: SavedPlan[] = [
  { id: '1', name: 'Summer Europe', destination: 'Switzerland', date: 'Jul 2024', price: '$2,400', thumbnail: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200&h=150&fit=crop' },
  { id: '2', name: 'Winter Getaway', destination: 'Iceland', date: 'Dec 2023', price: '$1,800', thumbnail: 'https://images.unsplash.com/photo-1504681869696-d977e92a32a0?w=200&h=150&fit=crop' },
];

export const mockReports: Report[] = [
  { id: '1', title: 'Travel Summary 2024', date: 'Jan 2024', icon: '📊', description: 'Annual travel report and spending analysis' },
  { id: '2', title: 'Best Deals Found', date: 'This Month', icon: '💰', description: 'Top 10 flight deals and hotel offers' },
];

export const mockRecommendedHotels: RecommendedHotel[] = [
  {
    id: '1',
    rank: 1,
    name: 'Marina Bay Sands',
    nights: 4,
    price: 1280,
    image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=80&h=80&fit=crop',
  },
  {
    id: '2',
    rank: 2,
    name: 'The Fullerton Hotel, Singapore',
    nights: 4,
    price: 1040,
    image: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=80&h=80&fit=crop',
  },
];
