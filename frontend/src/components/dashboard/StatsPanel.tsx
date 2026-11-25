import React from 'react';
import { useDatasetStore } from '../../stores/datasetStore';

export const StatsPanel: React.FC = () => {
  const { metadata } = useDatasetStore();

  // Helper to display value or placeholder
  const display = (value: unknown) => (value !== undefined && value !== null ? String(value) : '—');

  const rowCount = metadata?.row_count;
  const colCount = metadata?.column_count;
  const target = metadata?.target_column;
  // No additional metrics are provided by the store beyond those in DatasetMetadata.
  // Placeholders will be shown for any unavailable values.
  const missingValues = null;
  const duplicateRows = null;

  return (
    <section className="my-8">
      <h2 className="text-2xl font-bold text-black mb-4">Dataset Statistics</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        <div className="p-4 bg-cream border border-black rounded-xl text-black">
          <div className="text-sm text-orange font-semibold mb-1">Rows</div>
          <div className="text-xl font-bold">{display(rowCount)}</div>
        </div>
        <div className="p-4 bg-cream border border-black rounded-xl text-black">
          <div className="text-sm text-orange font-semibold mb-1">Columns</div>
          <div className="text-xl font-bold">{display(colCount)}</div>
        </div>
        <div className="p-4 bg-cream border border-black rounded-xl text-black">
          <div className="text-sm text-orange font-semibold mb-1">Target Column</div>
          <div className="text-xl font-bold">{display(target)}</div>
        </div>
        <div className="p-4 bg-cream border border-black rounded-xl text-black">
          <div className="text-sm text-orange font-semibold mb-1">Missing Values</div>
          <div className="text-xl font-bold">{display(missingValues)}</div>
        </div>
        <div className="p-4 bg-cream border border-black rounded-xl text-black">
          <div className="text-sm text-orange font-semibold mb-1">Duplicate Rows</div>
          <div className="text-xl font-bold">{display(duplicateRows)}</div>
        </div>
      </div>
    </section>
  );
};

