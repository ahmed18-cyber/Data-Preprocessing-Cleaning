import React, { useState } from 'react';
import { Download, FileSpreadsheet, Database, Loader2, AlertCircle, Check } from 'lucide-react';
import { downloadProcessedData, downloadAuditReport } from '../../api/exportApi';

interface Props {
  sessionId: string;
}

export function ExportPanel({ sessionId }: Props) {
  const [loading, setLoading] = useState(''); // '' | 'train' | 'test' | 'report'
  const [error, setError] = useState('');

  const handleDownload = async (type: 'train' | 'test' | 'report') => {
    setLoading(type);
    setError('');
    try {
      if (type === 'report') {
        await downloadAuditReport(sessionId);
      } else {
        await downloadProcessedData(sessionId, type);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed.');
    } finally {
      setLoading('');
    }
  };

  // Editorial file panel for training / testing datasets
  const DatasetPanel = (
    type: 'train' | 'test',
    index: string,
    title: string,
    description: string,
    format: string,
    Icon: React.ReactNode,
    indexColor: string,
    panelBg: string
  ) => (
    <div className={`relative rounded border-3 ${panelBg} p-6 shadow-[2px_2px_0px_0px_#000000]`}> // panel
      {/* Large index number */}
      <div className={`absolute -top-4 -right-4 text-9xl font-bold ${indexColor} opacity-10`}>{index}</div>
      <div className="flex items-start gap-4">
        <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${indexColor} text-white`}>{Icon}</div>
        <div className="flex-1">
          <h3 className="font-bold text-black text-lg mb-1">{title}</h3>
          <p className="text-sm text-black/70 mb-1">{description}</p>
          <p className="text-xs text-black/50">Format: {format}</p>
        </div>
      </div>
      <button
        onClick={() => handleDownload(type)}
        disabled={loading !== ''}
        className="mt-4 flex items-center justify-center gap-2 rounded border-3 bg-[#FF4400] px-4 py-2.5 text-sm font-medium text-white hover:bg-[#FF4400]/90 disabled:opacity-50"
      >
        {loading === type ? (
          <Loader2 className="animate-spin" size={17} />
        ) : (
          <Download size={17} />
        )}
        Download
      </button>
    </div>
  );

  // Central audit report feature block
  const AuditReportBlock = () => (
    <div className="relative rounded border-3 bg-[#0047AB] p-6 shadow-[2px_2px_0px_0px_#000000] text-white">
      <div className="absolute -top-4 -right-4 text-9xl font-bold text-white opacity-10">03</div>
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-white/20 text-white">
          <FileSpreadsheet size={24} />
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-white text-lg mb-1">Audit Report</h3>
          <p className="text-sm text-white/80 mb-1">
            Complete Excel audit of all preprocessing actions, decisions and transformations.
          </p>
          <p className="text-xs text-white/70">Format: XLSX</p>
        </div>
      </div>
      <button
        onClick={() => handleDownload('report')}
        disabled={loading !== ''}
        className="mt-4 flex items-center justify-center gap-2 rounded border-3 bg-[#FF4400] px-4 py-2.5 text-sm font-medium text-white hover:bg-[#FF4400]/90 disabled:opacity-50"
      >
        {loading === 'report' ? (
          <Loader2 className="animate-spin" size={17} />
        ) : (
          <Download size={17} />
        )}
        Download
      </button>
    </div>
  );

  return (
    <div className="space-y-12 bg-cream p-8">
      {/* HERO – split composition */}
      <section className="flex flex-col md:flex-row items-start gap-8">
        {/* Left side – text */}
        <div className="flex-1 space-y-4">
          <div className="text-xs font-mono uppercase text-[#0047AB]">DATA LAB / FINAL STATION</div>
          <h1 className="text-5xl font-extrabold text-black leading-tight">DATA IS READY</h1>
          <p className="text-lg text-black/70 max-w-xl">
            All preprocessing steps have been executed successfully. Export the final artifacts for downstream use.
          </p>
          <div className="flex items-center gap-2 text-black/70">
            <Check size={20} className="text-[#0047AB]" />
            <span>Preprocessing completed – data is clean and ready.</span>
          </div>
        </div>
        {/* Right side – graphic composition */}
        <div className="flex-1 relative flex items-center justify-center min-h-[200px]">
          {/* Stacked icons to suggest files */}
          <div className="absolute left-0 top-0 transform -rotate-6 bg-[#FF4400]/10 rounded-md p-4">
            <Database size={48} className="text-[#FF4400]" />
          </div>
          <div className="absolute right-0 bottom-0 transform rotate-6 bg-[#0047AB]/10 rounded-md p-4">
            <FileSpreadsheet size={48} className="text-[#0047AB]" />
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <Database size={64} className="text-[#FF4400]" />
          </div>
        </div>
      </section>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 rounded border-3 border-red-600 bg-cream p-4 text-sm text-red-700">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* Export panels */}
      <section className="grid gap-8 md:grid-cols-2">
        {/* Training dataset */}
        {DatasetPanel(
          'train',
          '01',
          'Training Dataset',
          'Processed training data ready for model ingestion.',
          'CSV',
          <Database size={24} />, // orangeish icon background handled in panel
          'text-[#FF4400]',
          'bg-cream'
        )}
        {/* Testing dataset */}
        {DatasetPanel(
          'test',
          '02',
          'Testing Dataset',
          'Processed testing data for evaluation.',
          'CSV',
          <Database size={24} />, // cobalt icon background handled in panel
          'text-[#0047AB]',
          'bg-cream'
        )}
      </section>

      {/* Audit report feature block */}
      <section>{AuditReportBlock()}</section>
    </div>
  );
}
