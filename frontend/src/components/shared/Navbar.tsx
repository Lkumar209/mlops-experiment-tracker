import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/experiments', label: 'Experiments' },
    { path: '/gpu-monitor', label: 'GPU Monitor' },
  ];

  return (
    <nav style={{ background: '#1e293b', borderBottom: '1px solid #334155', padding: '0 24px', display: 'flex', alignItems: 'center', gap: 32, height: 56 }}>
      <span style={{ color: '#7c3aed', fontWeight: 800, fontSize: 18 }}>MLOps Tracker</span>
      {navItems.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          style={{
            color: location.pathname === item.path ? '#818cf8' : '#94a3b8',
            textDecoration: 'none',
            fontWeight: location.pathname === item.path ? 600 : 400,
            fontSize: 14,
          }}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
};
