import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Users, 
  Calendar, 
  Settings, 
  Activity,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

export function Dashboard() {
  const [stats, setStats] = useState({
    agents: { total: 0, active: 0 },
    meetings: { total: 0, active: 0, upcoming: 0 },
    configurations: { total: 0, active: 0 }
  })
  const [recentMeetings, setRecentMeetings] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch stats from multiple endpoints
      const [agentStats, meetingStats, upcomingMeetings] = await Promise.all([
        fetch('http://localhost:5000/api/agents/stats').then(r => r.json()),
        fetch('http://localhost:5000/api/meetings/stats').then(r => r.json()),
        fetch('http://localhost:5000/api/meetings/upcoming?limit=5').then(r => r.json())
      ])

      if (agentStats.success) {
        setStats(prev => ({ ...prev, agents: agentStats.data }))
      }

      if (meetingStats.success) {
        setStats(prev => ({ ...prev, meetings: meetingStats.data }))
      }

      if (upcomingMeetings.success) {
        setRecentMeetings(upcomingMeetings.data)
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: 'Total Agents',
      value: stats.agents.total_agents || 0,
      subtitle: `${stats.agents.active_agents || 0} active`,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Active Meetings',
      value: stats.meetings.active_meetings || 0,
      subtitle: `${stats.meetings.scheduled_meetings || 0} scheduled`,
      icon: Calendar,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Total Meetings',
      value: stats.meetings.total_meetings || 0,
      subtitle: `${stats.meetings.completed_meetings || 0} completed`,
      icon: Activity,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Recent Activity',
      value: stats.meetings.recent_meetings_7_days || 0,
      subtitle: 'Last 7 days',
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ]

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-gray-500">{stat.subtitle}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Meetings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Upcoming Meetings</span>
            </CardTitle>
            <CardDescription>
              Next scheduled meetings for your agents
            </CardDescription>
          </CardHeader>
          <CardContent>
            {recentMeetings.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No upcoming meetings</p>
              </div>
            ) : (
              <div className="space-y-4">
                {recentMeetings.map((meeting) => (
                  <div key={meeting.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{meeting.title}</h4>
                      <p className="text-sm text-gray-500">
                        {new Date(meeting.scheduled_start).toLocaleString()}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant="outline" className="text-xs">
                          {meeting.platform}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {meeting.participants.length} participants
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {meeting.status === 'scheduled' && (
                        <Badge variant="secondary">
                          <Clock className="w-3 h-3 mr-1" />
                          Scheduled
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button className="w-full justify-start" variant="outline">
              <Users className="w-4 h-4 mr-2" />
              Create New Agent
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Calendar className="w-4 h-4 mr-2" />
              Schedule Meeting
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Settings className="w-4 h-4 mr-2" />
              Configure Platform
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Activity className="w-4 h-4 mr-2" />
              View Analytics
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>System Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <div>
                <p className="font-medium">API Server</p>
                <p className="text-sm text-gray-500">Online</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <div>
                <p className="font-medium">Database</p>
                <p className="text-sm text-gray-500">Connected</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-yellow-500" />
              <div>
                <p className="font-medium">Speech Services</p>
                <p className="text-sm text-gray-500">Checking...</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

