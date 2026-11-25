import React from 'react';
import { Database, Binary, Hash, HelpCircle, Copy, HardDrive } from 'lucide-react';
import type { DatasetOverview } from '../../types/eda';

interface OverviewCardsProps {
  overview: DatasetOverview;
}

export const OverviewCards: React.FC<OverviewCardsProps> = ({ overview }) => {
  const cards = [
    {
      code: 'OBS // 01',
      label: 'Total Observations',
      value: (overview.total_rows ?? 0).toLocaleString(),
      subtext: `${(overview.total_columns ?? 0).toLocaleString()} Features detected`,
      icon: Database,
      accentBorder: 'border-l-4 border-l-black',
      tagColor: 'bg-black text-white',
      valueColor: 'text-black',
      iconColor: 'text-black',
    },
    {
      code: 'NUM // 02',
      label: 'Numerical Features',
      value: (overview.numerical_columns_count ?? 0).toString(),
      subtext: `${overview.boolean_columns_count ?? 0} Boolean flags`,
      icon: Hash,
      accentBorder: 'border-l-4 border-l-cobalt',
      tagColor: 'bg-cobalt text-white',
      valueColor: 'text-cobalt',
      iconColor: 'text-cobalt',
    },
    {
      code: 'CAT // 03',
      label: 'Categorical & Text',
      value: ((overview.categorical_columns_count ?? 0) + (overview.text_columns_count ?? 0)).toString(),
      subtext: `${overview.datetime_columns_count ?? 0} Datetime features`,
      icon: Binary,
      accentBorder: 'border-l-4 border-l-black',
      tagColor: 'bg-white text-black border border-black',
      valueColor: 'text-black',
      iconColor: 'text-black',
    },
    {
      code: 'NULL // 04',
      label: 'Missing Values',
      value: (overview.total_missing_cells ?? 0).toLocaleString(),
      subtext: `${overview.missing_cells_percentage ?? 0}% cell missingness`,
      icon: HelpCircle,
      accentBorder: (overview.total_missing_cells ?? 0) > 0 ? 'border-l-4 border-l-orange' : 'border-l-4 border-l-black',
      tagColor: (overview.total_missing_cells ?? 0) > 0 ? 'bg-orange text-white' : 'bg-white text-black border border-black',
      valueColor: (overview.total_missing_cells ?? 0) > 0 ? 'text-orange' : 'text-black',
      iconColor: (overview.total_missing_cells ?? 0) > 0 ? 'text-orange' : 'text-black/60',
    },
    {
      code: 'DUP // 05',
      label: 'Duplicate Records',
      value: (overview.total_duplicate_rows ?? 0).toLocaleString(),
      subtext: `${overview.duplicate_rows_percentage ?? 0}% duplicate rate`,
      icon: Copy,
      accentBorder: (overview.total_duplicate_rows ?? 0) > 0 ? 'border-l-4 border-l-red-600' : 'border-l-4 border-l-black',
      tagColor: (overview.total_duplicate_rows ?? 0) > 0 ? 'bg-red-600 text-white' : 'bg-white text-black border border-black',
      valueColor: (overview.total_duplicate_rows ?? 0) > 0 ? 'text-red-600' : 'text-black',
      iconColor: (overview.total_duplicate_rows ?? 0) > 0 ? 'text-red-600' : 'text-black/60',
    },
    {
      code: 'MEM // 06',
      label: 'RAM Footprint',
      value: overview.memory_usage_formatted || '—',
      subtext: `${(overview.memory_usage_bytes ?? 0).toLocaleString()} bytes`,
      icon: HardDrive,
      accentBorder: 'border-l-4 border-l-cobalt',
      tagColor: 'bg-cream text-black border border-black',
      valueColor: 'text-black',
      iconColor: 'text-cobalt',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4 select-none">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div
            key={idx}
            className={`p-3.5 sm:p-4 bg-cream border-2 sm:border-3 border-black ${c.accentBorder} shadow-[4px_4px_0px_0px_#000000] hover:shadow-[2px_2px_0px_0px_#000000] hover:translate-x-[2px] hover:translate-y-[2px] transition-all flex flex-col justify-between`}
          >
            {/* Top row: technical code badge and icon */}
            <div className="flex items-center justify-between gap-1 mb-3">
              <span className={`text-[9px] font-mono font-black uppercase px-1.5 py-0.5 ${c.tagColor}`}>
                {c.code}
              </span>
              <Icon className={`h-4 w-4 ${c.iconColor} stroke-[2.5] shrink-0`} />
            </div>

            {/* Middle: prominent editorial value */}
            <div className="space-y-1">
              <div className="text-[11px] font-mono font-bold uppercase tracking-wider text-black/70 truncate" title={c.label}>
                {c.label}
              </div>
              <div className={`text-2xl sm:text-3xl font-black font-mono tracking-tight ${c.valueColor} truncate`} title={c.value}>
                {c.value}
              </div>
            </div>

            {/* Bottom: technical subtext badge */}
            <div className="mt-3 pt-2 border-t-2 border-black/15 font-mono text-[10px] font-semibold text-black/75 truncate" title={c.subtext}>
              {c.subtext}
            </div>
          </div>
        );
      })}
    </div>
  );
};
