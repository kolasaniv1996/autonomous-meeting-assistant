import { Menu, Bell, User } from 'lucide-react'
import { Button } from '@/components/ui/button'

const pageNames = {
  '/dashboard': 'Dashboard',
  '/configurations': 'Configurations',
  '/agents': 'Agents',
  '/meetings': 'Meetings',
  '/settings': 'Settings'
}

export function Header({ sidebarOpen, setSidebarOpen, currentPage }) {
  const pageName = pageNames[window.location.pathname] || 'Dashboard'

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </Button>
          
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">{pageName}</h1>
            <p className="text-sm text-gray-500">
              Manage your autonomous agents and meetings
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            <Bell className="w-5 h-5" />
          </Button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-blue-600" />
            </div>
            <span className="text-sm font-medium text-gray-700">Admin</span>
          </div>
        </div>
      </div>
    </header>
  )
}

