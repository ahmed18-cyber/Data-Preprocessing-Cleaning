import React, { useState } from 'react';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';

import { Hero } from './components/dashboard/Hero';
import { StatsPanel } from './components/dashboard/StatsPanel';
import { FileDropzone } from './components/ingestion/FileDropzone';
import { DatasetConfigPanel } from './components/ingestion/DatasetConfigPanel';
import { PreviewTable } from './components/ingestion/PreviewTable';
import { EDADashboard } from './components/eda/EDADashboard';
import { RecommendationsPanel } from './components/recommendations/RecommendationsPanel';
import { PreprocessingPanel } from './components/preprocessing/PreprocessingPanel';
import { ExportPanel } from './components/export/ExportPanel';

import { useDatasetStore } from './stores/datasetStore';

import {
  Eye,
  BarChart2,
  Lightbulb,
  Settings2,
  Download,
} from 'lucide-react';

type Tab =
  | 'preview'
  | 'eda'
  | 'recommendations'
  | 'preprocessing'
  | 'export';

export const App: React.FC = () => {
  const { sessionId } = useDatasetStore();
  const [activeTab, setActiveTab] = useState<Tab>('preview');

 [] = [
    {
      id: 'preview',
      label: 'Dataset Setup & Preview',
      icon: <Eye size={16} />,
      phase: 'Phase 1',
    },
    {
      id: 'eda',
      label: 'Exploratory Data Analysis',
      icon: <BarChart2 size={16} />,
      phase: 'Phase 2',
    },
    {
      id: 'recommendations',
      label: 'Recommendations',
      icon: <Lightbulb size={16} />,
      phase: 'Phase 3',
    },
    {
      id: 'preprocessing',
      label: 'Preprocessing',
      icon: <Settings2 size={16} />,
      phase: 'Phase 4',
    },
    {
      id: 'export',
      label: 'Export',
      icon: <Download size={16} />,
      phase: 'Phase 5',
    },
  ];

  return (
    <div className="min-h-screen bg-cream text-black flex flex-col font-sans">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar activeTab={activeTab} setActiveTab={(tab) => setActiveTab(tab as any)} />
        <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-6 overflow-y-auto">
          {!sessionId ? (
            <>
              <Hero />
              <StatsPanel />
              <FileDropzone />
            </>
          ) : (
            <div className="space-y-6">
              {/* Active phase content */}
              {activeTab === 'preview' && (
                <div className="space-y-6">
                  <DatasetConfigPanel />
                  <PreviewTable />
                </div>
              )}

              {activeTab === 'eda' && (
                <EDADashboard />
              )}

              {activeTab === 'recommendations' && (
                <RecommendationsPanel sessionId={sessionId} />
              )}

              {activeTab === 'preprocessing' && (
                <PreprocessingPanel sessionId={sessionId} />
              )}

              {activeTab === 'export' && (
                <ExportPanel sessionId={sessionId} />
              )}
            </div>
          )}
        </main>
      </div>

      <footer className="bg-cream border-t border-black py-2 text-xs text-black/70 flex justify-between items-center px-6">
        <div>© 2026 DATA LAB{sessionId ? ` • Session: ${sessionId}` : ''}</div>
        <div>Generic Data Preprocessing & Cleaning Web Application</div>
        <div>5‑PHASE INTELLIGENT WORKFLOW</div>
      </footer>
    </div>
  );
};

export default App;
