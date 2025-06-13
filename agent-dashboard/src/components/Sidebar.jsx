import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Settings, 
  Users, 
  Calendar, 
  FileText,
  Menu,
  X,
  Bot
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Configurations', href: '/configurations', icon: FileText },
  { name: 'Agents', href: '/agents', icon: Users },
  { name: 'Meetings', href: '/meetings', icon: Calendar },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar({ open, setOpen }) {
  const location = useLocation()

  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 flex flex-col bg-white border-r border-gray-200 transition-all duration-300
        ${open ? 'w-64' : 'w-16'} lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Bot className="w-8 h-8 text-blue-600" />
            {open && (
              <span className="text-xl font-bold text-gray-900">
                Agent Dashboard
              </span>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setOpen(!open)}
            className="lg:hidden"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors
                  ${isActive 
                    ? 'bg-blue-100 text-blue-900' 
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }
                `}
              >
                <item.icon className={`
                  flex-shrink-0 w-5 h-5 transition-colors
                  ${isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'}
                  ${open ? 'mr-3' : 'mx-auto'}
                `} />
                {open && item.name}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          {open ? (
            <div className="text-xs text-gray-500">
              <p>Autonomous Agent Framework</p>
              <p>v2.0.0</p>
            </div>
          ) : (
            <div className="flex justify-center">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

