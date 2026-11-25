import React from 'react';
import type { InferredType } from '../../types/dataset';

interface TypeBadgeProps {
  type: InferredType;
}

export const TypeBadge: React.FC<TypeBadgeProps> = ({ type }) => {
  const styles: Record<InferredType, string> = {
    numeric: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    categorical: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    datetime: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    boolean: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    text: 'bg-slate-500/10 text-slate-300 border-slate-500/20',
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${styles[type] || styles.text}`}
    >
      {type}
    </span>
  );
};
