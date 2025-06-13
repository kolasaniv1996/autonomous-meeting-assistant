import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Header } from './components/Header'
import { Dashboard } from './pages/Dashboard'
import { Configurations } from './pages/Configurations'
import { Agents } from './pages/Agents'
import { Meetings } from './pages/Meetings'
import { Settings } from './pages/Settings'
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState('dashboard')

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Sidebar 
          open={sidebarOpen} 
          setOpen={setSidebarOpen}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
        />
        
        <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-16'}`}>
          <Header 
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
            currentPage={currentPage}
          />
          
          <main className="p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/configurations" element={<Configurations />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/meetings" element={<Meetings />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App

