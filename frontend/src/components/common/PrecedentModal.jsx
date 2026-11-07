import React, { useState, useMemo } from 'react';
import { X, Search, Sparkles, Database, ShieldCheck, Cpu, ArrowUpRight, CheckCircle2 } from 'lucide-react';

const SEEDED_PRECEDENTS = [
  {
    id: 'PREC-INR-001',
    category: 'INR',
    categoryLabel: 'Item Not Received',
    title: 'FedEx Direct Signature Match at PayPal Confirmed Address',
    summary: 'Buyer claimed item never arrived. Carrier tracking proved delivery with recipient surname signature matching billing address.',
    winRate: '94.8%',
    similarity: '0.942',
    outcome: 'WON',
    features: ['GPS Geofence Match', 'Direct Signature (S. Jenkins)', 'Address Validation §11.3'],
    vectorPreview: [0.0382, -0.0194, 0.0812, 0.0045, -0.0521, 0.0418, 0.0129, -0.0763],
  },
  {
    id: 'PREC-INR-004',
    category: 'INR',
    categoryLabel: 'Item Not Received',
    title: 'UPS Proof of Delivery with Photo & Porch Geofence',
    summary: 'Buyer filed non-receipt claim. Logistics telemetry provided high-res delivery photo timestamped within estimated delivery window.',
    winRate: '91.2%',
    similarity: '0.915',
    outcome: 'WON',
    features: ['Proof of Delivery Photo', 'Carrier Time Window', 'Seller Protection Qualified'],
    vectorPreview: [0.0215, -0.0418, 0.0761, 0.0182, -0.0319, 0.0592, 0.0084, -0.0611],
  },
  {
    id: 'PREC-UNAUTH-002',
    category: 'UNAUTHORIZED',
    categoryLabel: 'Unauthorized Transaction',
    title: 'PayPal One-Touch Checkout with 3D Secure IP Match',
    summary: 'Buyer claimed card was used without authorization. Evidence proved device fingerprint and 2FA SMS confirmation matched account profile.',
    winRate: '88.4%',
    similarity: '0.887',
    outcome: 'WON',
    features: ['One-Touch Device Fingerprint', 'IP/Geolocation Match', 'PayPal Token Auth'],
    vectorPreview: [-0.0118, 0.0532, 0.0621, -0.0294, -0.0441, 0.0329, 0.0187, -0.0489],
  },
  {
    id: 'PREC-SNAD-003',
    category: 'SNAD',
    categoryLabel: 'Significantly Not As Described',
    title: 'Exact SKU Serial Number & Condition Specification Match',
    summary: 'Buyer argued item received was incorrect color variant. Warehouse packing scan proved shipped unit matched purchased SKU specification.',
    winRate: '82.6%',
    similarity: '0.864',
    outcome: 'WON',
    features: ['SKU Barcode Verification', 'Listing Specification Match', 'Return Policy Enforced'],
    vectorPreview: [0.0412, -0.0287, 0.0543, 0.0319, -0.0187, 0.0482, -0.0125, -0.0534],
  },
  {
    id: 'PREC-INR-008',
    category: 'INR',
    categoryLabel: 'Item Not Received',
    title: 'Buyer Rescheduling Notice Accepted via Carrier Portal',
    summary: 'Buyer requested hold at FedEx facility then filed dispute before pickup. Carrier log confirmed package ready for collection.',
    winRate: '86.1%',
    similarity: '0.841',
    outcome: 'WON',
    features: ['Carrier Hold Request Log', 'Buyer Initiated Redirection', 'Customer Portal Audit'],
    vectorPreview: [0.0189, -0.0354, 0.0691, 0.0123, -0.0412, 0.0387, 0.0094, -0.0578],
  },
  {
    id: 'PREC-UNAUTH-006',
    category: 'UNAUTHORIZED',
    categoryLabel: 'Unauthorized Transaction',
    title: 'Digital Goods Download Log with Verified Merchant Login',
    summary: 'Disputed digital SaaS activation key. Server access logs confirmed software license was activated from buyer registered email address.',
    winRate: '85.0%',
    similarity: '0.835',
    outcome: 'WON',
    features: ['Software Key Activation Timestamp', 'Buyer Account Audit Log', 'Non-Refundable Policy'],
    vectorPreview: [-0.0084, 0.0471, 0.0589, -0.0198, -0.0384, 0.0298, 0.0142, -0.0419],
  },
];

export default function PrecedentModal({ isOpen, onClose }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [expandedVectorId, setExpandedVectorId] = useState(null);

  const filteredPrecedents = useMemo(() => {
    return SEEDED_PRECEDENTS.filter((item) => {
      const matchesCat = selectedCategory === 'ALL' || item.category === selectedCategory;
      const q = searchQuery.toLowerCase().trim();
      const matchesSearch =
        !q ||
        item.title.toLowerCase().includes(q) ||
        item.summary.toLowerCase().includes(q) ||
        item.id.toLowerCase().includes(q) ||
        item.features.some((f) => f.toLowerCase().includes(q));
      return matchesCat && matchesSearch;
    });
  }, [searchQuery, selectedCategory]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
      <div
        className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-slate-50 to-blue-50/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00457C] to-[#0079C1] flex items-center justify-center text-white shadow-xs">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-900">RAG Precedent Retrieval Engine</h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-[#00457C] border border-blue-200">
                  Dense Vector Space
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Elasticsearch 1536-dimensional cosine similarity indexing over 32 historical PayPal dispute precedents
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Metric Bar */}
        <div className="px-6 py-3 bg-slate-50 border-b border-slate-100 grid grid-cols-3 gap-4 text-center">
          <div className="p-2 bg-white rounded-xl border border-slate-200/80 shadow-2xs">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Indexed Precedents</span>
            <span className="text-lg font-black text-[#00457C]">32 Cases</span>
          </div>
          <div className="p-2 bg-white rounded-xl border border-slate-200/80 shadow-2xs">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Historical Win Rate</span>
            <span className="text-lg font-black text-emerald-600">78.1% Alpha</span>
          </div>
          <div className="p-2 bg-white rounded-xl border border-slate-200/80 shadow-2xs">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Embedding Dimension</span>
            <span className="text-lg font-black text-[#0079C1]">1,536-dim Dense</span>
          </div>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="px-6 py-3 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search precedents by keyword, tracking, carrier, or defense strategy..."
              className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-[#0079C1] focus:border-transparent transition-all"
            />
          </div>
          <div className="flex items-center gap-1.5">
            {[
              { id: 'ALL', label: 'All Precedents' },
              { id: 'INR', label: 'Item Not Received' },
              { id: 'SNAD', label: 'Not As Described' },
              { id: 'UNAUTHORIZED', label: 'Unauthorized' },
            ].map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                  selectedCategory === cat.id
                    ? 'bg-[#0079C1] text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Precedents List */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
          {filteredPrecedents.length === 0 ? (
            <div className="py-12 text-center text-slate-500">
              <Cpu className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p className="text-sm font-semibold">No matching vector precedents found</p>
              <p className="text-xs text-slate-400 mt-1">Try broadening your search term</p>
            </div>
          ) : (
            filteredPrecedents.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-xl border border-slate-200 hover:border-blue-300 bg-white transition-all shadow-xs hover:shadow-sm"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                        {item.id}
                      </span>
                      <span className="text-xs font-semibold text-slate-500">
                        • {item.categoryLabel}
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-slate-900">{item.title}</h3>
                    <p className="text-xs text-slate-600 mt-1 leading-relaxed">{item.summary}</p>
                  </div>

                  <div className="text-right shrink-0">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Outcome: {item.outcome} ({item.winRate})
                    </span>
                    <span className="block text-[11px] font-mono text-[#0079C1] font-bold mt-1">
                      Cosine Sim: {item.similarity}
                    </span>
                  </div>
                </div>

                {/* Evidence Features */}
                <div className="mt-3 flex flex-wrap items-center gap-1.5 pt-2.5 border-t border-slate-100">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1">
                    Key Telemetry:
                  </span>
                  {item.features.map((feat, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded bg-blue-50 border border-blue-100 text-[11px] font-medium text-[#00457C]"
                    >
                      {feat}
                    </span>
                  ))}
                  <button
                    onClick={() =>
                      setExpandedVectorId(expandedVectorId === item.id ? null : item.id)
                    }
                    className="ml-auto text-[11px] text-[#0079C1] hover:underline font-semibold flex items-center gap-1"
                  >
                    <span>{expandedVectorId === item.id ? 'Hide Vector' : 'Inspect 1536-dim Vector'}</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                </div>

                {/* Collapsible Vector Payload */}
                {expandedVectorId === item.id && (
                  <div className="mt-2.5 p-2.5 bg-slate-900 rounded-lg text-slate-200 font-mono text-[10px] leading-relaxed overflow-x-auto border border-slate-800">
                    <div className="text-slate-400 mb-1 flex items-center justify-between">
                      <span># Embedding Float32 Array Preview (text-embedding-3-small)</span>
                      <span className="text-emerald-400">Normalized L2 = 1.000</span>
                    </div>
                    [{item.vectorPreview.join(', ')}, ... 1,528 dimensions truncated]
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#0079C1]" />
            <span>
              Real-time LangChain RAG pipeline matches incoming webhooks against this vector index in &lt;15ms.
            </span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold transition-all text-xs"
          >
            Close Explorer
          </button>
        </div>
      </div>
    </div>
  );
}
