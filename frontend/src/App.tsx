import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/shared/Navbar';
import { Dashboard } from './components/Dashboard/Dashboard';
import { ExperimentList } from './components/ExperimentList/ExperimentList';
import { RunDetail } from './components/RunDetail/RunDetail';
import { GPUMonitor } from './components/GPUMonitor/GPUMonitor';

const App: React.FC = () => (
  <BrowserRouter>
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <main style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/experiments" element={<div style={{ padding: 24 }}><ExperimentList /></div>} />
          <Route path="/runs/:runId" element={<RunDetail />} />
          <Route path="/gpu-monitor" element={<GPUMonitor />} />
        </Routes>
      </main>
    </div>
  </BrowserRouter>
);

export default App;
