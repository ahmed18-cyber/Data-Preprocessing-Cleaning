import React from 'react';
import type { LucideIcon } from 'lucide-react';
import { Database, BarChart3, Lightbulb, Settings, Download } from 'lucide-react';

type NavItem = {
  id: string;
  label: string;
  icon: LucideIcon;
};

export const Sidebar: React.FC<{ activeTab: string; setActiveTab: (tab: any) => void }> = ({ activeTab, setActiveTab }) => {
  const navItems: NavItem[] = [
    { id: 'preview', label: 'Dataset', icon: Database },
    { id: 'eda', label: 'Exploration', icon: BarChart3 },
    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
    { id: 'preprocessing', label: 'Preprocess', icon: Settings },
    { id: 'export', label: 'Export', icon: Download },
  ];

  return (
    <aside className="w-64 bg-cream border-r border-black hidden md:block">
      <div className="p-4 flex flex-col h-full">
        <div className="mb-8 text-2xl font-bold text-black">DATA LAB</div>
        <nav className="flex-1 space-y-2">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-2 w-full px-3 py-2 rounded-md text-sm font-medium transition-colors 
                ${activeTab === item.id ? 'bg-orange text-white' : 'text-black hover:bg-orange/20'}
              `}
            >
              {React.createElement(item.icon, { size: 16, className: 'stroke-current' })}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="mt-8 text-xs text-black/60">© 2026 Data Lab</div>
      </div>
    </aside>
  );
};

