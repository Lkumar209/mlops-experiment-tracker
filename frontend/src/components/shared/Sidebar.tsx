import React from 'react';
import { NavLink } from 'react-router-dom';

const links = [
  { path: '/', label: 'Dashboard', icon: '⬛' },
  { path: '/experiments', label: 'Experiments', icon: '🧪' },
  { path: '/gpu-monitor', label: 'GPU Monitor', icon: '⚡' },
];

export const Sidebar: React.FC = () => (
  <aside style={{ width: 220, background: '#1e293b', borderRight: '1px solid #334155', minHeight: '100vh', padding: '24px 0' }}>
    {links.map((link) => (
      <NavLink
        key={link.path}
        to={link.path}
        end
        style={({ isActive }) => ({
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '10px 20px',
          color: isActive ? '#818cf8' : '#94a3b8',
          background: isActive ? '#7c3aed22' : 'transparent',
          textDecoration: 'none',
          fontSize: 14,
          fontWeight: isActive ? 600 : 400,
          borderLeft: isActive ? '3px solid #7c3aed' : '3px solid transparent',
        })}
      >
        <span>{link.icon}</span>
        {link.label}
      </NavLink>
    ))}
  </aside>
);
