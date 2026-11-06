import React, { useState, useEffect } from 'react';
import TopNav from './TopNav';
import Sidebar from './Sidebar';

export default function Layout({
  children,
  currentView = 'queue',
  onSelectView,
  isWsConnected = true,
  lastMessage = null,
}) {
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false);

  // Close sidebar on ESC key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isSidebarExpanded) {
        setIsSidebarExpanded(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isSidebarExpanded]);

  return (
    <div className="h-screen w-screen flex flex-col bg-slate-50 text-slate-900 overflow-hidden font-sans">
      {/* Top Navigation Bar with View Tabs and Live Controls */}
      <TopNav
        currentView={currentView}
        onSelectView={onSelectView}
        isWsConnected={isWsConnected}
        isSidebarExpanded={isSidebarExpanded}
        onToggleSidebar={() => setIsSidebarExpanded(!isSidebarExpanded)}
      />

      {/* Main Container: Central Viewport + Collapsible Slide-over Stream */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Workspace Central Viewport */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6">
          <div className="max-w-[1600px] mx-auto space-y-6">
            {children}
          </div>
        </main>

        {/* Collapsible Right Slide-over Sidebar: Agent Telemetry Stream */}
        <Sidebar
          isExpanded={isSidebarExpanded}
          onToggle={() => setIsSidebarExpanded(!isSidebarExpanded)}
          lastMessage={lastMessage}
        />
      </div>
    </div>
  );
}
