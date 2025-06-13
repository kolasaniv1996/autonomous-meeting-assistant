import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, Calendar, Settings as SettingsIcon, Activity, Clock, CheckCircle } from 'lucide-react';

const Dashboard = () => {
  const { token, user } = useAuth();
  const [stats, setStats] = useState({
    totalAgents: 0,
    activeAgents: 0,
    totalMeetings: 0,
    upcomingMeetings: 0,
    configurations: 0
  });
  const [recentMeetings, setRecentMeetings] = useState([]);
  const [agentStatus, setAgentStatus] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_BASE = 'http://localhost:8080/api';

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch agents
      const agentsResponse = await fetch(`${API_BASE}/agents`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const agentsData = await agentsResponse.json();
      
      // Fetch meetings
      const meetingsResponse = await fetch(`${API_BASE}/meetings`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const meetingsData = await meetingsResponse.json();
      
      // Fetch configurations
      const configResponse = await fetch(`${API_BASE}/configurations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const configData = await configResponse.json();

      const agents = agentsData.agents || [];
      const meetings = meetingsData.meetings || [];
      const configurations = configData.configurations || [];

      // Calculate stats
      const now = new Date();
      const upcomingMeetings = meetings.filter(m => new Date(m.scheduled_start) > now);
      const activeAgents = agents.filter(a => a.status === 'active');

      setStats({
        totalAgents: agents.length,
        activeAgents: activeAgents.length,
        totalMeetings: meetings.length,
        upcomingMeetings: upcomingMeetings.length,
        configurations: configurations.length
      });

      // Recent meetings (last 5)
      const sortedMeetings = meetings
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);
      setRecentMeetings(sortedMeetings);

      // Agent status distribution
      const statusCounts = agents.reduce((acc, agent) => {
        acc[agent.status] = (acc[agent.status] || 0) + 1;
        return acc;
      }, {});

      const statusData = Object.entries(statusCounts).map(([status, count]) => ({
        name: status,
        value: count
      }));
      setAgentStatus(statusData);

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    const colors = {
      active: '#22c55e',
      inactive: '#6b7280',
      busy: '#f59e0b',
      error: '#ef4444'
    };
    return colors[status] || '#6b7280';
  };

  const getMeetingStatusBadge = (meeting) => {
    const now = new Date();
    const startTime = new Date(meeting.scheduled_start);
    const endTime = new Date(startTime.getTime() + (meeting.duration * 60000));

    if (meeting.status === 'cancelled') {
      return <Badge variant="destructive">Cancelled</Badge>;
    }
    if (now < startTime) {
      return <Badge variant="outline">Scheduled</Badge>;
    }
    if (now >= startTime && now <= endTime) {
      return <Badge variant="default">In Progress</Badge>;
    }
    return <Badge variant="secondary">Completed</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back, {user?.username}!</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAgents}</div>
            <p className="text-xs text-muted-foreground">
              {stats.activeAgents} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeAgents}</div>
            <p className="text-xs text-muted-foreground">
              Currently running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Meetings</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalMeetings}</div>
            <p className="text-xs text-muted-foreground">
              All time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.upcomingMeetings}</div>
            <p className="text-xs text-muted-foreground">
              Scheduled meetings
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Configurations</CardTitle>
            <SettingsIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.configurations}</div>
            <p className="text-xs text-muted-foreground">
              Setup profiles
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Agent Status Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Agent Status Distribution</CardTitle>
            <CardDescription>Current status of all agents</CardDescription>
          </CardHeader>
          <CardContent>
            {agentStatus.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={agentStatus}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {agentStatus.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getStatusColor(entry.name)} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-48 text-muted-foreground">
                No agents configured
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Meetings</CardTitle>
            <CardDescription>Latest scheduled meetings</CardDescription>
          </CardHeader>
          <CardContent>
            {recentMeetings.length > 0 ? (
              <div className="space-y-3">
                {recentMeetings.map((meeting) => (
                  <div key={meeting.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{meeting.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDateTime(meeting.scheduled_start)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getMeetingStatusBadge(meeting)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-48 text-muted-foreground">
                No meetings scheduled
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and shortcuts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center gap-3">
                <Calendar className="h-8 w-8 text-primary" />
                <div>
                  <h3 className="font-medium">Schedule Meeting</h3>
                  <p className="text-sm text-muted-foreground">Create a new meeting</p>
                </div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center gap-3">
                <Users className="h-8 w-8 text-primary" />
                <div>
                  <h3 className="font-medium">Add Agent</h3>
                  <p className="text-sm text-muted-foreground">Configure new agent</p>
                </div>
              </div>
            </div>
            
            <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center gap-3">
                <SettingsIcon className="h-8 w-8 text-primary" />
                <div>
                  <h3 className="font-medium">Setup Config</h3>
                  <p className="text-sm text-muted-foreground">Add API credentials</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

