import React, { useCallback, useMemo, useRef, useState, useEffect } from 'react';
import axios from 'axios';
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import { AllEnterpriseModule } from 'ag-grid-enterprise';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';
import '../../styles/ag-grid-theme.css';

// Register all Community and Enterprise modules for AG Grid v36 SSRM & Master-Detail
ModuleRegistry.registerModules([AllCommunityModule, AllEnterpriseModule]);

import DisputeTypeRenderer from './renderers/DisputeTypeRenderer';
import ConfidenceRenderer from './renderers/ConfidenceRenderer';
import ActionCellRenderer from './renderers/ActionCellRenderer';
import DisputeDetail from './DisputeDetail';
import Badge from '../common/Badge';
import { Search, Filter, RefreshCw, RotateCcw } from 'lucide-react';

export default function DisputeGrid({ lastMessage }) {
  const gridRef = useRef(null);
  const [activeTab, setActiveTab] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [counts, setCounts] = useState({
    all: 0,
    review: 0,
    auto: 0,
    resolved: 0,
  });

  // Fetch live summary counts directly from the backend
  const fetchCounts = useCallback(async () => {
    try {
      const res = await axios.get('/api/analytics/summary');
      if (res.data) {
        const reviewCount = res.data.review_needed ?? 0;
        setCounts({
          all: res.data.total ?? res.data.total_disputes ?? 0,
          review: reviewCount,
          auto: res.data.auto_submitted ?? 0,
          resolved: res.data.resolved ?? 0,
        });

        // If no drafts are awaiting review (e.g. all were approved during testing), prime fresh demo drafts
        if (reviewCount === 0) {
          try {
            await axios.post('/api/disputes/reset-demo-data');
            const refreshed = await axios.get('/api/analytics/summary');
            if (refreshed.data) {
              setCounts({
                all: refreshed.data.total ?? refreshed.data.total_disputes ?? 0,
                review: refreshed.data.review_needed ?? 0,
                auto: refreshed.data.auto_submitted ?? 0,
                resolved: refreshed.data.resolved ?? 0,
              });
              if (gridRef.current?.api) {
                gridRef.current.api.refreshServerSide({ purge: false });
              }
            }
          } catch (primeErr) {
            // graceful fallback
          }
        }
      }
    } catch (err) {
      console.error('Failed to fetch analytics summary counts:', err);
    }
  }, []);

  const handleResetDrafts = async () => {
    try {
      await axios.post('/api/disputes/reset-demo-data');
      if (gridRef.current?.api) {
        gridRef.current.api.refreshServerSide({ purge: true });
      }
      fetchCounts();
    } catch (err) {
      console.warn('Failed to reset drafts:', err);
    }
  };

  useEffect(() => {
    fetchCounts();
  }, [fetchCounts]);

  // Handle real-time WebSocket events to refresh grid & counts
  useEffect(() => {
    if (!lastMessage) return;
    if (
      [
        'agent_decision',
        'new_dispute',
        'evidence_submitted',
        'dispute_resolved',
      ].includes(lastMessage.type)
    ) {
      if (gridRef.current && gridRef.current.api) {
        gridRef.current.api.refreshServerSide({ purge: false });
      }
      fetchCounts();
    }
  }, [lastMessage, fetchCounts]);

  // Server-Side Datasource for AG Grid SSRM
  const createServerSideDatasource = useCallback(() => {
    return {
      getRows: async (params) => {
        const { startRow = 0, endRow = 10, sortModel } = params.request;

        const sortCol = sortModel && sortModel.length > 0 ? sortModel[0].colId : null;
        const sortDir = sortModel && sortModel.length > 0 ? sortModel[0].sort : 'asc';

        try {
          const res = await axios.get('/api/disputes', {
            params: {
              start_row: startRow,
              end_row: endRow,
              sort_col: sortCol,
              sort_dir: sortDir,
              filter_tab: activeTab,
              search: searchQuery || undefined,
            },
          });

          const rows = res.data.rows || [];
          params.success({
            rowData: rows,
            rowCount: res.data.total_count,
          });
        } catch (err) {
          console.error('[SSRM] getRows error:', err);
          params.fail();
        }
      },
    };
  }, [activeTab, searchQuery]);

  const serverSideDatasource = useMemo(() => {
    return createServerSideDatasource();
  }, [createServerSideDatasource]);

  // Update server-side datasource whenever filter tab or search query changes
  useEffect(() => {
    if (gridRef.current && gridRef.current.api) {
      gridRef.current.api.setGridOption('serverSideDatasource', serverSideDatasource);
      gridRef.current.api.refreshServerSide({ purge: true });
    }
  }, [serverSideDatasource]);

  const handleTabClick = (tabId) => {
    setActiveTab(tabId);
    if (gridRef.current && gridRef.current.api) {
      gridRef.current.api.refreshServerSide({ purge: true });
    }
  };

  // Column Definitions
  const columnDefs = useMemo(
    () => [
      {
        field: 'paypal_dispute_id',
        headerName: 'Dispute ID',
        cellRenderer: 'agGroupCellRenderer',
        cellRendererParams: {
          innerRenderer: (p) => (
            <span className="font-mono font-bold text-[#00457C] hover:text-[#0079C1] transition-colors cursor-pointer">
              {p.value}
            </span>
          ),
        },
        minWidth: 190,
        flex: 1.2,
      },
      {
        field: 'reason',
        headerName: 'Reason Category',
        cellRenderer: DisputeTypeRenderer,
        minWidth: 220,
        flex: 1.3,
      },
      {
        field: 'dispute_amount',
        headerName: 'Disputed Amount',
        valueFormatter: (p) => (p.value !== undefined ? `$${Number(p.value).toFixed(2)}` : '$0.00'),
        cellClass: 'font-mono font-extrabold text-slate-900',
        minWidth: 130,
        flex: 0.9,
        sortable: true,
      },
      {
        field: 'agent_decision',
        headerName: 'Autonomous Agent Decision',
        cellRenderer: (p) => <Badge status={p.value} size="sm" />,
        minWidth: 190,
        flex: 1.2,
      },
      {
        field: 'confidence_score',
        headerName: 'AI Confidence',
        cellRenderer: ConfidenceRenderer,
        minWidth: 140,
        flex: 0.9,
        sortable: true,
      },
      {
        field: 'status',
        headerName: 'PayPal Status',
        cellRenderer: (p) => (
          <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wide">
            {p.value?.replace(/_/g, ' ') || 'UNDER REVIEW'}
          </span>
        ),
        minWidth: 140,
        flex: 0.9,
      },
      {
        field: 'response_deadline',
        headerName: 'Deadline',
        cellRenderer: (p) => {
          if (!p.value) return <span className="text-slate-400 font-mono text-xs">N/A</span>;
          try {
            const date = new Date(p.value);
            return (
              <span className="text-amber-700 font-mono font-semibold text-xs">
                {date.toLocaleDateString()}
              </span>
            );
          } catch {
            return <span className="text-slate-600 font-mono text-xs">{p.value}</span>;
          }
        },
        minWidth: 120,
        flex: 0.8,
      },
      {
        headerName: 'Action',
        cellRenderer: ActionCellRenderer,
        minWidth: 150,
        flex: 1,
        sortable: false,
      },
    ],
    []
  );

  const defaultColDef = useMemo(
    () => ({
      resizable: true,
      sortable: true,
      filter: false,
    }),
    []
  );

  const onGridReady = useCallback(
    (params) => {
      params.api.setGridOption('serverSideDatasource', serverSideDatasource);
    },
    [serverSideDatasource]
  );

  const handleManualRefresh = () => {
    if (gridRef.current?.api) {
      gridRef.current.api.refreshServerSide({ purge: false });
    }
    fetchCounts();
  };

  const filterTabs = [
    { id: 'ALL', label: 'All Disputes', count: counts.all },
    { id: 'REVIEW_NEEDED', label: 'Requires Review / Drafts', count: counts.review },
    { id: 'AUTO_SUBMITTED', label: 'Auto-Submitted', count: counts.auto },
    { id: 'RESOLVED', label: 'Resolved Precedents', count: counts.resolved },
  ];

  return (
    <div className="space-y-4">
      {/* Sub-Tabs and Search/Filter Controls Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        {/* Horizontal Sub-Tabs Row */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
          {filterTabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => handleTabClick(tab.id)}
                className={`px-3 py-1.5 rounded-lg transition-all flex items-center space-x-2 whitespace-nowrap text-xs ${
                  isActive
                    ? 'bg-blue-50 text-[#00457C] border border-blue-200 font-bold shadow-xs'
                    : 'bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 font-medium'
                }`}
              >
                <span>{tab.label}</span>
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold ${
                    isActive ? 'bg-[#0079C1] text-white' : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Live Search and Quick Action Toolbar */}
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search dispute ID, buyer email, order..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-[#0079C1] w-64 shadow-xs transition-all"
            />
          </div>

          <button
            onClick={handleManualRefresh}
            className="px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors flex items-center gap-1.5 shadow-xs"
            title="Refresh Dispute Queue"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
            <span className="hidden sm:inline">Refresh Queue</span>
          </button>

          <button
            onClick={handleResetDrafts}
            className="px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 border border-blue-200 text-xs font-semibold text-[#00457C] transition-colors flex items-center gap-1.5 shadow-xs"
            title="Reset demo dispute drafts for testing merchant review & sign-off"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#0079C1]" />
            <span className="hidden sm:inline">Reset Drafts (6)</span>
          </button>
        </div>
      </div>

      {/* AG Grid Enterprise Container (Light Quartz Theme) */}
      <div
        className="ag-theme-quartz w-full h-[580px] rounded-xl overflow-hidden border border-slate-200 bg-white shadow-xs"
        style={{ height: '580px', width: '100%', minHeight: '580px' }}
      >
        <AgGridReact
          ref={gridRef}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          rowModelType="serverSide"
          serverSideDatasource={serverSideDatasource}
          pagination={true}
          paginationPageSize={10}
          paginationPageSizeSelector={[10, 20, 50]}
          cacheBlockSize={10}
          maxBlocksInCache={10}
          masterDetail={true}
          detailCellRenderer={DisputeDetail}
          detailRowAutoHeight={true}
          animateRows={true}
          onGridReady={onGridReady}
        />
      </div>

      {/* Grid Status Footer Strip */}
      <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium px-1">
        <span>Showing active dispute cases • PayPal Sandbox Mirror: Realtime Live</span>
        <span className="text-slate-400 font-mono">AG Grid Enterprise SSRM</span>
      </div>
    </div>
  );
}
