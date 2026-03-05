'use client';

import React from 'react';

// ─── Inline text renderer ─────────────────────────────────────────────────────
// Handles **bold** and plain text within a single line.
function InlineText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**') ? (
          <strong key={i} className="font-semibold text-gray-900">
            {part.slice(2, -2)}
          </strong>
        ) : (
          <React.Fragment key={i}>{part}</React.Fragment>
        )
      )}
    </>
  );
}

// ─── Predicates ───────────────────────────────────────────────────────────────
const SECTION_HEADER_RE = /^([A-Z][A-Z &\-\/]{2,}):?\s*$/;
const DAY_LINE_RE = /^(Day\s+\d+\b[^:]*):?\s*(.*)/i;
const BULLET_RE = /^[\-•*]\s+(.+)/;
const NUMBERED_RE = /^(\d+)\.\s+(.+)/;
const TABLE_SEPARATOR_RE = /^[=\-]{10,}$/;
const HORIZONTAL_RULE_RE = /^---+$/;

// Icons for each known section
const SECTION_ICONS: Record<string, string> = {
  'FLIGHT & TRANSPORT': '✈️',
  'HOTEL OPTIONS': '🏨',
  'DAY-BY-DAY ITINERARY': '📅',
  'MUST-VISIT PLACES': '📍',
  'LOCAL TIPS': '💡',
  'TRIP SUMMARY': '📋',
  'HOTEL OPTIONS FOR': '🏨',
  'FLIGHT OPTIONS': '✈️',
};

function getSectionIcon(header: string): string {
  for (const key of Object.keys(SECTION_ICONS)) {
    if (header.toUpperCase().startsWith(key)) return SECTION_ICONS[key];
  }
  return '📌';
}

// ─── Day Card ─────────────────────────────────────────────────────────────────
function DayCard({ label, content }: { label: string; content: string }) {
  const dayNumMatch = label.match(/\d+/);
  const dayNum = dayNumMatch ? dayNumMatch[0] : '?';
  // Extract date if present in the label e.g. "Day 1 — Date: 2026-03-10"
  const dateMatch = label.match(/Date:\s*([\d\-]+)/i) || label.match(/—\s*([\d]{4}-[\d]{2}-[\d]{2})/);
  const dateStr = dateMatch ? dateMatch[1] : null;
  const baseLabel = label.replace(/—.*$/, '').trim();

  return (
    <div className="flex gap-3 my-2">
      {/* Day number badge */}
      <div className="flex-shrink-0 flex flex-col items-center">
        <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center shadow-sm">
          <span className="text-white text-xs font-bold">{dayNum}</span>
        </div>
        <div className="w-px flex-1 bg-blue-100 my-1 min-h-[12px]" />
      </div>
      <div className="flex-1 pb-3">
        <div className="flex items-baseline gap-2 flex-wrap">
          <span className="text-sm font-semibold text-blue-700">{baseLabel}</span>
          {dateStr && (
            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{dateStr}</span>
          )}
        </div>
        {content && (
          <p className="text-sm text-gray-700 mt-1 leading-relaxed">
            <InlineText text={content} />
          </p>
        )}
      </div>
    </div>
  );
}

// ─── Bullet list ─────────────────────────────────────────────────────────────
function BulletItem({ text }: { text: string }) {
  return (
    <li className="flex gap-2 text-sm text-gray-700 leading-relaxed py-0.5">
      <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
      <span><InlineText text={text} /></span>
    </li>
  );
}

function NumberedItem({ num, text }: { num: string; text: string }) {
  return (
    <li className="flex gap-2 text-sm text-gray-700 leading-relaxed py-0.5">
      <span className="flex-shrink-0 w-5 h-5 rounded-full bg-orange-100 text-orange-700 text-xs font-bold flex items-center justify-center mt-0.5">{num}</span>
      <span><InlineText text={text} /></span>
    </li>
  );
}

// ─── Section wrapper ──────────────────────────────────────────────────────────
function Section({ header, children }: { header: string; children: React.ReactNode }) {
  const icon = getSectionIcon(header);
  return (
    <div className="mt-4 first:mt-0">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-base">{icon}</span>
        <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wide">{header}</h3>
      </div>
      <div className="pl-6">{children}</div>
    </div>
  );
}

// ─── Divider ─────────────────────────────────────────────────────────────────
function Divider() {
  return <hr className="my-4 border-t border-gray-200" />;
}

// ─── Main parser & renderer ──────────────────────────────────────────────────
export default function FormattedMessage({ text }: { text: string }) {
  if (!text) return null;

  // Split the full text into major blocks separated by `---`
  const majorBlocks = text.split(/\n(?:---+)\n/);

  return (
    <div className="text-sm text-gray-800 space-y-1 w-full">
      {majorBlocks.map((block, blockIdx) => (
        <React.Fragment key={blockIdx}>
          {blockIdx > 0 && <Divider />}
          <BlockContent text={block} />
        </React.Fragment>
      ))}
    </div>
  );
}

// ─── Block content parser ─────────────────────────────────────────────────────
function BlockContent({ text }: { text: string }) {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];

  let i = 0;
  let currentSection: string | null = null;
  let sectionChildren: React.ReactNode[] = [];
  let listItems: React.ReactNode[] = [];
  let listType: 'bullet' | 'numbered' | null = null;

  const flushList = () => {
    if (listItems.length > 0) {
      const tag = listType === 'numbered' ? (
        <ol key={`list-${elements.length}`} className="space-y-0.5 mb-2">{listItems}</ol>
      ) : (
        <ul key={`list-${elements.length}`} className="space-y-0.5 mb-2">{listItems}</ul>
      );
      if (currentSection !== null) {
        sectionChildren.push(tag);
      } else {
        elements.push(tag);
      }
      listItems = [];
      listType = null;
    }
  };

  const flushSection = () => {
    if (currentSection !== null) {
      elements.push(
        <Section key={`sec-${elements.length}`} header={currentSection}>
          {sectionChildren}
        </Section>
      );
      currentSection = null;
      sectionChildren = [];
    }
  };

  const pushLine = (node: React.ReactNode) => {
    if (currentSection !== null) {
      sectionChildren.push(node);
    } else {
      elements.push(node);
    }
  };

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // Skip table separator lines (====== or ------)
    if (TABLE_SEPARATOR_RE.test(trimmed)) { i++; continue; }

    // Horizontal rule inside a block (not the major `---` splits)
    if (HORIZONTAL_RULE_RE.test(trimmed)) {
      flushList();
      flushSection();
      elements.push(<Divider key={`div-${i}`} />);
      i++; continue;
    }

    // Empty line = flush list, optionally flush section
    if (trimmed === '') {
      flushList();
      i++; continue;
    }

    // Section header (e.g. "FLIGHT & TRANSPORT:", "HOTEL OPTIONS:")
    const secMatch = SECTION_HEADER_RE.exec(trimmed);
    if (secMatch) {
      flushList();
      flushSection();
      currentSection = secMatch[1] || trimmed.replace(/:$/, '');
      i++; continue;
    }

    // Day line (e.g. "Day 1 — Date: 2026-03-10: Activities...")
    const dayMatch = DAY_LINE_RE.exec(trimmed);
    if (dayMatch) {
      flushList();
      const label = dayMatch[1].trim();
      const content = dayMatch[2].trim();
      const node = <DayCard key={`day-${i}`} label={label} content={content} />;
      pushLine(node);
      i++; continue;
    }

    // Bullet line
    const bulletMatch = BULLET_RE.exec(trimmed);
    if (bulletMatch) {
      if (listType !== 'bullet') { flushList(); listType = 'bullet'; }
      listItems.push(<BulletItem key={`b-${i}`} text={bulletMatch[1]} />);
      i++; continue;
    }

    // Numbered list line
    const numberedMatch = NUMBERED_RE.exec(trimmed);
    if (numberedMatch) {
      if (listType !== 'numbered') { flushList(); listType = 'numbered'; }
      listItems.push(<NumberedItem key={`n-${i}`} num={numberedMatch[1]} text={numberedMatch[2]} />);
      i++; continue;
    }

    // Table-like lines (e.g. " 1    Grand Hotel   4.8/5  $200/night  Paris")
    // These are lines with multiple consecutive spaces acting as column separators
    if (/\s{3,}/.test(trimmed) && !trimmed.startsWith('Day') && !/^[A-Z]/.test(trimmed.slice(5))) {
      flushList();
      const node = (
        <p key={`tbl-${i}`} className="text-xs font-mono text-gray-600 bg-gray-50 px-3 py-0.5 rounded leading-relaxed whitespace-pre">
          {trimmed}
        </p>
      );
      pushLine(node);
      i++; continue;
    }

    // Plain paragraph line — group consecutive plain lines together
    flushList();
    const plainLines: string[] = [trimmed];
    while (i + 1 < lines.length) {
      const next = lines[i + 1].trim();
      if (
        next === '' ||
        SECTION_HEADER_RE.test(next) ||
        DAY_LINE_RE.test(next) ||
        BULLET_RE.test(next) ||
        NUMBERED_RE.test(next) ||
        TABLE_SEPARATOR_RE.test(next) ||
        HORIZONTAL_RULE_RE.test(next)
      ) break;
      plainLines.push(next);
      i++;
    }
    const node = (
      <p key={`p-${i}`} className="text-sm text-gray-700 leading-relaxed mb-1">
        <InlineText text={plainLines.join(' ')} />
      </p>
    );
    pushLine(node);
    i++;
  }

  flushList();
  flushSection();

  return <>{elements}</>;
}
