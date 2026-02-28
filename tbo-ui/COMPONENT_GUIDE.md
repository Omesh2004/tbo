# Travel Assistant UI - Component Guide

## Overview

This is a fully responsive, dynamic travel assistant interface built with Next.js 16, React 19, Tailwind CSS, and shadcn/ui. All components are designed to accept dynamic data through props, making them easy to integrate with backend services.

## Project Structure

```
/components
  ├── Header.tsx              # Top navigation bar
  ├── Sidebar.tsx             # Left sidebar with history, plans, reports
  ├── ChatArea.tsx            # Chat message interface
  ├── AgentResponse.tsx       # Agent message component
  ├── HotelOptions.tsx        # Hotel cards display
  ├── TransportOptions.tsx    # Transport options display
  └── QuotePanel.tsx          # Right panel with pricing and recommendations

/lib
  ├── types.ts                # TypeScript interfaces for all data types
  └── mockData.ts             # Mock data for development

/app
  └── page.tsx                # Main page integrating all components
```

## Component Documentation

### 1. Header Component
**File:** `components/Header.tsx`

Displays the top navigation bar with logo, navigation buttons, and CTA.

**Props:**
```typescript
interface HeaderProps {
  logoSrc?: string;           // Logo image URL
  onMenuClick?: () => void;   // Mobile menu toggle handler
  onHistoryClick?: () => void;
  onSavedPlansClick?: () => void;
}
```

**Usage:**
```tsx
<Header 
  logoSrc="your-logo-url"
  onMenuClick={handleMenuClick}
/>
```

---

### 2. Sidebar Component
**File:** `components/Sidebar.tsx`

Left sidebar with agent profile, tabbed navigation (History/Plans/Reports), and map.

**Props:**
```typescript
interface SidebarProps {
  history: HistoryItem[];          // Trip history items
  savedPlans: SavedPlan[];         // Saved travel plans
  reports: Report[];               // Travel reports
  agent: Agent;                    // Agent profile info
  isOpen?: boolean;                // Show/hide sidebar (mobile)
}
```

**Usage:**
```tsx
<Sidebar
  history={mockHistory}
  savedPlans={mockSavedPlans}
  reports={mockReports}
  agent={mockAgent}
  isOpen={sidebarOpen}
/>
```

**Data Types (lib/types.ts):**
```typescript
- HistoryItem: id, date, destination, thumbnail
- SavedPlan: id, name, destination, date, price, thumbnail
- Report: id, title, date, icon, description
- Agent: id, name, title, image, bio
```

---

### 3. ChatArea Component
**File:** `components/ChatArea.tsx`

Chat interface with message display and input area.

**Props:**
```typescript
interface ChatAreaProps {
  messages: ChatMessage[];         // Array of chat messages
  onSendMessage?: (message: string) => void;
  placeholder?: string;            // Input placeholder text
}
```

**Usage:**
```tsx
<ChatArea
  messages={messages}
  onSendMessage={handleSendMessage}
  placeholder="What would you like to explore next?"
/>
```

**Data Types:**
```typescript
ChatMessage: {
  id: string;
  sender: 'user' | 'agent';
  avatar?: string;
  name?: string;
  message: string;
  timestamp?: string;
}
```

---

### 4. AgentResponse Component
**File:** `components/AgentResponse.tsx`

Styled agent message component with profile info.

**Props:**
```typescript
interface AgentResponseProps {
  agent: Agent;                    // Agent info
  message: string;                 // Response text
  actionText?: string;             // CTA button text
  onAction?: () => void;           // CTA handler
}
```

---

### 5. HotelOptions Component
**File:** `components/HotelOptions.tsx`

Grid display of hotel cards with ratings, amenities, and pricing.

**Props:**
```typescript
interface HotelOptionsProps {
  title?: string;                      // Section title
  hotels: HotelOption[];               // Hotel cards data
  onSelectHotel?: (hotelId: string) => void;
  selectedHotelId?: string;            // Track selected hotel
}
```

**Usage:**
```tsx
<HotelOptions
  hotels={mockHotels}
  selectedHotelId={selectedHotel}
  onSelectHotel={setSelectedHotel}
/>
```

**Data Types:**
```typescript
HotelOption: {
  id: string;
  name: string;
  image: string;
  rating: number;
  reviewCount: number;
  price: number;
  priceUnit: string;           // '/night', 'per day', etc.
  amenities: string[];         // ['WiFi', 'Pool', 'Gym']
  cancellation: boolean;
  tier: 'basic' | 'standard' | 'premium';
}
```

---

### 6. TransportOptions Component
**File:** `components/TransportOptions.tsx`

Transport options display with icons and pricing.

**Props:**
```typescript
interface TransportOptionsProps {
  title?: string;                         // Section title
  options: TransportOption[];
  onSelectTransport?: (transportId: string) => void;
  selectedTransportId?: string;
}
```

**Usage:**
```tsx
<TransportOptions
  options={mockTransport}
  selectedTransportId={selectedTransport}
  onSelectTransport={setSelectedTransport}
/>
```

**Data Types:**
```typescript
TransportOption: {
  id: string;
  name: string;
  icon?: string;
  duration: string;            // '35-40 min'
  price: number;
  priceUnit?: string;          // 'per person', 'flat rate'
  description?: string;        // 'Sedan', 'SUV'
  type: 'shuttle' | 'car' | 'train' | 'bus';
}
```

---

### 7. QuotePanel Component
**File:** `components/QuotePanel.tsx`

Right panel displaying pricing breakdown, quote summary, and hotel recommendations.

**Props:**
```typescript
interface QuotePanelProps {
  quote: QuoteSummary;
  recommendedHotels?: RecommendedHotel[];
  onGeneratePDF?: () => void;
  onViewDetails?: () => void;
}
```

**Usage:**
```tsx
<QuotePanel
  quote={mockQuote}
  recommendedHotels={mockRecommendedHotels}
  onGeneratePDF={handleGeneratePDF}
/>
```

**Data Types:**
```typescript
QuoteSummary: {
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

RecommendedHotel: {
  id: string;
  rank: number;
  name: string;
  nights: number;
  price: number;
  image?: string;
}
```

---

## Type Definitions

All type definitions are centralized in `lib/types.ts`:

### Core Types:
- `Trip` - Trip configuration
- `HistoryItem` - Past searches/bookings
- `SavedPlan` - Saved itineraries
- `HotelOption` - Hotel details
- `TransportOption` - Transport methods
- `QuoteSummary` - Pricing information
- `Agent` - Travel agent profile
- `ChatMessage` - Chat communication
- `Report` - Travel reports
- `RecommendedHotel` - Top picks

---

## Mock Data

Mock data is available in `lib/mockData.ts` with:
- `mockAgent` - Sample agent profile
- `mockChatMessages` - Sample chat history
- `mockHotels` - 3 hotel options
- `mockTransport` - 2 transport options
- `mockQuote` - Sample pricing
- `mockHistory` - 3 past trips
- `mockSavedPlans` - 2 saved plans
- `mockReports` - 2 reports
- `mockRecommendedHotels` - 2 recommended hotels

---

## Responsive Design

All components are fully responsive with breakpoints:
- **Mobile (< 768px):** Single column, drawer sidebar
- **Tablet (768px - 1024px):** Two-column layout, sidebar always visible
- **Desktop (> 1024px):** Three-column layout with full sidebar

Tailwind classes used:
- `md:` - Tablet breakpoint (768px)
- `lg:` - Desktop breakpoint (1024px)

---

## Key Features

✅ **Dynamic Data:** All content controlled via props
✅ **Responsive:** Mobile → Tablet → Desktop
✅ **Type-Safe:** Full TypeScript support
✅ **Modular:** Easy to modify and extend
✅ **Accessible:** Semantic HTML and ARIA attributes
✅ **Styled:** Tailwind CSS + shadcn/ui components
✅ **Interactive:** Selection states, hover effects
✅ **PDF Ready:** Generate PDF button prepared for jsPDF integration

---

## Integration Guide

### 1. Replace Mock Data with Backend Data

```tsx
// Instead of:
import { mockHotels } from '@/lib/mockData';

// Fetch from API:
const [hotels, setHotels] = useState([]);
useEffect(() => {
  fetch('/api/hotels').then(res => res.json()).then(setHotels);
}, []);

<HotelOptions hotels={hotels} />
```

### 2. Implement PDF Generation

The `QuotePanel` has `onGeneratePDF` handler ready:

```tsx
import jsPDF from 'jspdf';

const handleGeneratePDF = () => {
  const doc = new jsPDF();
  // Add quote content to PDF
  doc.save('quote.pdf');
};

<QuotePanel onGeneratePDF={handleGeneratePDF} />
```

### 3. Add State Management

For complex state across components, add SWR or Redux:

```tsx
import useSWR from 'swr';

function Home() {
  const { data: hotels } = useSWR('/api/hotels', fetcher);
  const { data: quote } = useSWR('/api/quote', fetcher);
  
  return (
    <HotelOptions hotels={hotels} />
  );
}
```

---

## Customization

### Update Colors
Edit design tokens in `tailwind.config.ts` and `app/globals.css`

### Modify Component Styling
All components use Tailwind CSS. Adjust classes for quick styling changes.

### Change Layout
Modify breakpoints in components (e.g., change `md:w-96` to `md:w-80`)

### Add New Features
Create new components following the same pattern and add to the main page.

---

## Future Enhancements

- [ ] PDF generation with jsPDF
- [ ] Real-time availability integration
- [ ] User authentication
- [ ] Booking flow
- [ ] Payment integration
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Dark mode

---

## Troubleshooting

**Images not loading?**
- Ensure image URLs are publicly accessible
- Update image URLs in mockData.ts

**Layout issues on mobile?**
- Check tailwind responsive classes (md:, lg:)
- Test in browser DevTools mobile view

**Components not updating?**
- Ensure parent component re-renders on state change
- Check prop dependencies

---

## Support

For questions or issues, refer to:
- Component-level documentation in each file
- TypeScript interfaces in `lib/types.ts`
- Mock data examples in `lib/mockData.ts`
