import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Users, Video, Trash2, Plus, Save, Edit } from 'lucide-react';

const Meetings = () => {
  const { token } = useAuth();
  const [meetings, setMeetings] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingMeeting, setEditingMeeting] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    platform: '',
    meeting_url: '',
    scheduled_start: '',
    duration: 60,
    status: 'scheduled',
    assigned_agents: []
  });

  const API_BASE = 'http://localhost:8080/api';

  const platforms = [
    'Microsoft Teams',
    'Google Meet',
    'Zoom',
    'Webex',
    'Other'
  ];

  const statusColors = {
    scheduled: 'bg-blue-500',
    in_progress: 'bg-green-500',
    completed: 'bg-gray-500',
    cancelled: 'bg-red-500'
  };

  useEffect(() => {
    fetchMeetings();
    fetchAgents();
  }, []);

  const fetchMeetings = async () => {
    try {
      const response = await fetch(`${API_BASE}/meetings`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMeetings(data.meetings);
      } else {
        setError('Failed to fetch meetings');
      }
    } catch (error) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_BASE}/agents`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAgents(data.agents.filter(agent => agent.status === 'active'));
      }
    } catch (error) {
      console.error('Failed to fetch agents');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const url = editingMeeting 
        ? `${API_BASE}/meetings/${editingMeeting.id}`
        : `${API_BASE}/meetings`;
      
      const method = editingMeeting ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setSuccess(editingMeeting ? 'Meeting updated successfully' : 'Meeting scheduled successfully');
        setShowForm(false);
        setEditingMeeting(null);
        resetForm();
        fetchMeetings();
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to save meeting');
      }
    } catch (error) {
      setError('Network error occurred');
    }
  };

  const handleDelete = async (meetingId) => {
    if (!confirm('Are you sure you want to delete this meeting?')) return;

    try {
      const response = await fetch(`${API_BASE}/meetings/${meetingId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setSuccess('Meeting deleted successfully');
        fetchMeetings();
      } else {
        setError('Failed to delete meeting');
      }
    } catch (error) {
      setError('Network error occurred');
    }
  };

  const handleEdit = (meeting) => {
    setEditingMeeting(meeting);
    setFormData({
      title: meeting.title,
      description: meeting.description || '',
      platform: meeting.platform || '',
      meeting_url: meeting.meeting_url || '',
      scheduled_start: meeting.scheduled_start ? new Date(meeting.scheduled_start).toISOString().slice(0, 16) : '',
      duration: meeting.duration || 60,
      status: meeting.status,
      assigned_agents: meeting.assigned_agents || []
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      platform: '',
      meeting_url: '',
      scheduled_start: '',
      duration: 60,
      status: 'scheduled',
      assigned_agents: []
    });
  };

  const generateMeetingUrl = () => {
    if (formData.platform === 'Microsoft Teams') {
      setFormData(prev => ({
        ...prev,
        meeting_url: 'https://teams.microsoft.com/l/meetup-join/19%3ameeting_' + Math.random().toString(36).substr(2, 9)
      }));
    } else if (formData.platform === 'Google Meet') {
      setFormData(prev => ({
        ...prev,
        meeting_url: 'https://meet.google.com/' + Math.random().toString(36).substr(2, 10)
      }));
    } else if (formData.platform === 'Zoom') {
      setFormData(prev => ({
        ...prev,
        meeting_url: 'https://zoom.us/j/' + Math.floor(Math.random() * 1000000000)
      }));
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getMeetingStatus = (meeting) => {
    const now = new Date();
    const startTime = new Date(meeting.scheduled_start);
    const endTime = new Date(startTime.getTime() + (meeting.duration * 60000));

    if (meeting.status === 'cancelled') return 'cancelled';
    if (now < startTime) return 'scheduled';
    if (now >= startTime && now <= endTime) return 'in_progress';
    return 'completed';
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Meetings</h1>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Schedule Meeting
        </Button>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="mb-4">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {showForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>
              {editingMeeting ? 'Edit Meeting' : 'Schedule New Meeting'}
            </CardTitle>
            <CardDescription>
              Create a new meeting and assign agents for automated participation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Meeting Title</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., Weekly Standup"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="platform">Platform</Label>
                  <Select value={formData.platform} onValueChange={(value) => setFormData(prev => ({ ...prev, platform: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select platform" />
                    </SelectTrigger>
                    <SelectContent>
                      {platforms.map((platform) => (
                        <SelectItem key={platform} value={platform}>
                          {platform}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Meeting agenda and description"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="scheduled_start">Scheduled Start</Label>
                  <Input
                    id="scheduled_start"
                    type="datetime-local"
                    value={formData.scheduled_start}
                    onChange={(e) => setFormData(prev => ({ ...prev, scheduled_start: e.target.value }))}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="duration">Duration (minutes)</Label>
                  <Input
                    id="duration"
                    type="number"
                    min="15"
                    max="480"
                    value={formData.duration}
                    onChange={(e) => setFormData(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="meeting_url">Meeting URL</Label>
                  {formData.platform && formData.platform !== 'Other' && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={generateMeetingUrl}
                    >
                      Generate URL
                    </Button>
                  )}
                </div>
                <Input
                  id="meeting_url"
                  value={formData.meeting_url}
                  onChange={(e) => setFormData(prev => ({ ...prev, meeting_url: e.target.value }))}
                  placeholder="https://..."
                />
              </div>

              <div className="space-y-2">
                <Label>Assign Agents</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {agents.map((agent) => (
                    <div key={agent.id} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`agent-${agent.id}`}
                        checked={formData.assigned_agents.includes(agent.id)}
                        onChange={(e) => {
                          const agentIds = e.target.checked
                            ? [...formData.assigned_agents, agent.id]
                            : formData.assigned_agents.filter(id => id !== agent.id);
                          setFormData(prev => ({ ...prev, assigned_agents: agentIds }));
                        }}
                      />
                      <Label htmlFor={`agent-${agent.id}`} className="text-sm">
                        {agent.name}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit">
                  <Save className="w-4 h-4 mr-2" />
                  {editingMeeting ? 'Update' : 'Schedule'} Meeting
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowForm(false);
                    setEditingMeeting(null);
                    resetForm();
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {meetings.map((meeting) => {
          const currentStatus = getMeetingStatus(meeting);
          
          return (
            <Card key={meeting.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${statusColors[currentStatus]}`}></div>
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {meeting.title}
                        <Badge variant="outline">{currentStatus.replace('_', ' ')}</Badge>
                        {meeting.platform && (
                          <Badge variant="secondary">{meeting.platform}</Badge>
                        )}
                      </CardTitle>
                      <CardDescription>{meeting.description}</CardDescription>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(meeting)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(meeting.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>{formatDateTime(meeting.scheduled_start)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>{meeting.duration} minutes</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    <span>{meeting.assigned_agents?.length || 0} agents assigned</span>
                  </div>
                  {meeting.meeting_url && (
                    <div className="flex items-center gap-2">
                      <Video className="w-4 h-4" />
                      <a 
                        href={meeting.meeting_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary hover:underline truncate"
                      >
                        Join Meeting
                      </a>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {meetings.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-muted-foreground">No meetings found. Schedule your first meeting to get started.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Meetings;

