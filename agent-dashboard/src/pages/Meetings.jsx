import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Plus, 
  Edit, 
  Trash2, 
  Save, 
  X, 
  Calendar, 
  Search,
  Filter,
  Play,
  Square,
  Clock,
  CheckCircle,
  Users,
  Mic,
  MicOff,
  Video,
  VideoOff,
  FileText,
  Download
} from 'lucide-react'

export function Meetings() {
  const [meetings, setMeetings] = useState([])
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingMeeting, setEditingMeeting] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterPlatform, setFilterPlatform] = useState('')
  const [selectedMeeting, setSelectedMeeting] = useState(null)
  const [showTranscript, setShowTranscript] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    platform: 'teams',
    meeting_url: '',
    participants: [],
    scheduled_start: '',
    duration_minutes: 60,
    speech_provider: 'azure',
    enable_transcription: true
  })
  const [stats, setStats] = useState({})

  useEffect(() => {
    fetchMeetings()
    fetchAgents()
    fetchStats()
  }, [])

  const fetchMeetings = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/meetings')
      const data = await response.json()
      if (data.success) {
        setMeetings(data.data)
      }
    } catch (error) {
      console.error('Error fetching meetings:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/agents')
      const data = await response.json()
      if (data.success) {
        setAgents(data.data.filter(agent => agent.is_active))
      }
    } catch (error) {
      console.error('Error fetching agents:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/meetings/stats')
      const data = await response.json()
      if (data.success) {
        setStats(data.data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleCreateMeeting = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/meetings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      const data = await response.json()
      if (data.success) {
        setMeetings([data.data, ...meetings])
        setShowCreateForm(false)
        resetForm()
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error creating meeting:', error)
    }
  }

  const handleUpdateMeeting = async (meetingId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/meetings/${meetingId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      const data = await response.json()
      if (data.success) {
        setMeetings(meetings.map(meeting => 
          meeting.id === meetingId ? data.data : meeting
        ))
        setEditingMeeting(null)
        resetForm()
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error updating meeting:', error)
    }
  }

  const handleDeleteMeeting = async (meetingId) => {
    if (!confirm('Are you sure you want to delete this meeting?')) return
    
    try {
      const response = await fetch(`http://localhost:5000/api/meetings/${meetingId}`, {
        method: 'DELETE',
      })
      const data = await response.json()
      if (data.success) {
        setMeetings(meetings.filter(meeting => meeting.id !== meetingId))
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error deleting meeting:', error)
    }
  }

  const handleStartMeeting = async (meetingId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/meetings/${meetingId}/start`, {
        method: 'POST',
      })
      const data = await response.json()
      if (data.success) {
        setMeetings(meetings.map(meeting => 
          meeting.id === meetingId ? data.data : meeting
        ))
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error starting meeting:', error)
    }
  }

  const handleEndMeeting = async (meetingId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/meetings/${meetingId}/end`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          summary: 'Meeting completed successfully',
          action_items: []
        }),
      })
      const data = await response.json()
      if (data.success) {
        setMeetings(meetings.map(meeting => 
          meeting.id === meetingId ? data.data : meeting
        ))
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error ending meeting:', error)
    }
  }

  const fetchTranscript = async (meetingId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/meetings/${meetingId}/transcript`)
      const data = await response.json()
      if (data.success) {
        setSelectedMeeting(data.data)
        setShowTranscript(true)
      }
    } catch (error) {
      console.error('Error fetching transcript:', error)
    }
  }

  const startEditing = (meeting) => {
    setEditingMeeting(meeting.id)
    setFormData({
      title: meeting.title,
      description: meeting.description || '',
      platform: meeting.platform,
      meeting_url: meeting.meeting_url || '',
      participants: meeting.participants || [],
      scheduled_start: new Date(meeting.scheduled_start).toISOString().slice(0, 16),
      duration_minutes: meeting.duration_minutes || 60,
      speech_provider: meeting.speech_provider || 'azure',
      enable_transcription: meeting.enable_transcription
    })
  }

  const startCreating = () => {
    setShowCreateForm(true)
    resetForm()
  }

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      platform: 'teams',
      meeting_url: '',
      participants: [],
      scheduled_start: '',
      duration_minutes: 60,
      speech_provider: 'azure',
      enable_transcription: true
    })
  }

  const cancelEditing = () => {
    setEditingMeeting(null)
    setShowCreateForm(false)
    resetForm()
  }

  const filteredMeetings = meetings.filter(meeting => {
    const matchesSearch = meeting.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         meeting.description?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = !filterStatus || meeting.status === filterStatus
    const matchesPlatform = !filterPlatform || meeting.platform === filterPlatform
    
    return matchesSearch && matchesStatus && matchesPlatform
  })

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800'
      case 'active': return 'bg-green-100 text-green-800'
      case 'completed': return 'bg-gray-100 text-gray-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'scheduled': return <Clock className="w-3 h-3" />
      case 'active': return <Play className="w-3 h-3" />
      case 'completed': return <CheckCircle className="w-3 h-3" />
      default: return <Clock className="w-3 h-3" />
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Meetings</h2>
        </div>
        <div className="grid gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
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
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Meetings</h2>
          <p className="text-gray-600">Schedule and manage meetings</p>
        </div>
        <Button onClick={startCreating} disabled={showCreateForm || editingMeeting}>
          <Plus className="w-4 h-4 mr-2" />
          Schedule Meeting
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Meetings</p>
                <p className="text-2xl font-bold">{stats.total_meetings || 0}</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Meetings</p>
                <p className="text-2xl font-bold text-green-600">{stats.active_meetings || 0}</p>
              </div>
              <Play className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-gray-600">{stats.completed_meetings || 0}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-gray-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Scheduled</p>
                <p className="text-2xl font-bold text-blue-600">{stats.scheduled_meetings || 0}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search meetings by title or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <select
                className="px-3 py-2 border rounded-md"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <option value="">All Status</option>
                <option value="scheduled">Scheduled</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
              <select
                className="px-3 py-2 border rounded-md"
                value={filterPlatform}
                onChange={(e) => setFilterPlatform(e.target.value)}
              >
                <option value="">All Platforms</option>
                <option value="teams">Microsoft Teams</option>
                <option value="google_meet">Google Meet</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Create/Edit Form */}
      {(showCreateForm || editingMeeting) && (
        <Card>
          <CardHeader>
            <CardTitle>
              {showCreateForm ? 'Schedule New Meeting' : 'Edit Meeting'}
            </CardTitle>
            <CardDescription>
              {showCreateForm 
                ? 'Schedule a new meeting for your agents'
                : 'Modify the selected meeting'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <Label htmlFor="title">Meeting Title</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="e.g., Daily Standup"
                />
              </div>
              
              <div className="md:col-span-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Meeting description and agenda"
                  rows={3}
                />
              </div>
              
              <div>
                <Label htmlFor="platform">Platform</Label>
                <select
                  id="platform"
                  className="w-full p-2 border rounded-md"
                  value={formData.platform}
                  onChange={(e) => setFormData({...formData, platform: e.target.value})}
                >
                  <option value="teams">Microsoft Teams</option>
                  <option value="google_meet">Google Meet</option>
                </select>
              </div>
              
              <div>
                <Label htmlFor="meeting_url">Meeting URL (Optional)</Label>
                <Input
                  id="meeting_url"
                  value={formData.meeting_url}
                  onChange={(e) => setFormData({...formData, meeting_url: e.target.value})}
                  placeholder="https://teams.microsoft.com/..."
                />
              </div>
              
              <div>
                <Label htmlFor="scheduled_start">Scheduled Start</Label>
                <Input
                  id="scheduled_start"
                  type="datetime-local"
                  value={formData.scheduled_start}
                  onChange={(e) => setFormData({...formData, scheduled_start: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="duration_minutes">Duration (minutes)</Label>
                <Input
                  id="duration_minutes"
                  type="number"
                  value={formData.duration_minutes}
                  onChange={(e) => setFormData({...formData, duration_minutes: parseInt(e.target.value)})}
                  min="15"
                  max="480"
                />
              </div>
              
              <div>
                <Label htmlFor="speech_provider">Speech Provider</Label>
                <select
                  id="speech_provider"
                  className="w-full p-2 border rounded-md"
                  value={formData.speech_provider}
                  onChange={(e) => setFormData({...formData, speech_provider: e.target.value})}
                >
                  <option value="azure">Azure Speech Services</option>
                  <option value="google_cloud">Google Cloud Speech</option>
                  <option value="whisper">OpenAI Whisper</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="enable_transcription"
                  checked={formData.enable_transcription}
                  onChange={(e) => setFormData({...formData, enable_transcription: e.target.checked})}
                />
                <Label htmlFor="enable_transcription">Enable Transcription</Label>
              </div>
              
              <div className="md:col-span-2">
                <Label>Participants</Label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2 max-h-40 overflow-y-auto border rounded-md p-2">
                  {agents.map(agent => (
                    <label key={agent.id} className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={formData.participants.includes(agent.employee_id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              participants: [...formData.participants, agent.employee_id]
                            })
                          } else {
                            setFormData({
                              ...formData,
                              participants: formData.participants.filter(p => p !== agent.employee_id)
                            })
                          }
                        }}
                      />
                      <span>{agent.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4 border-t mt-4">
              <Button variant="outline" onClick={cancelEditing}>
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button 
                onClick={() => showCreateForm ? handleCreateMeeting() : handleUpdateMeeting(editingMeeting)}
              >
                <Save className="w-4 h-4 mr-2" />
                {showCreateForm ? 'Schedule' : 'Save'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Transcript Modal */}
      {showTranscript && selectedMeeting && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Meeting Transcript: {selectedMeeting.title}</CardTitle>
              <Button variant="outline" onClick={() => setShowTranscript(false)}>
                <X className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="max-h-96 overflow-y-auto bg-gray-50 p-4 rounded-md">
              {selectedMeeting.transcript && selectedMeeting.transcript.length > 0 ? (
                selectedMeeting.transcript.map((entry, index) => (
                  <div key={index} className="mb-2 p-2 bg-white rounded border">
                    <div className="text-sm text-gray-500 mb-1">
                      {entry.speaker} - {entry.timestamp}
                    </div>
                    <div>{entry.text}</div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center">No transcript available</p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Meetings List */}
      <div className="grid gap-4">
        {filteredMeetings.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {meetings.length === 0 ? 'No meetings found' : 'No meetings match your filters'}
              </h3>
              <p className="text-gray-500 mb-4">
                {meetings.length === 0 
                  ? 'Get started by scheduling your first meeting'
                  : 'Try adjusting your search or filter criteria'
                }
              </p>
              {meetings.length === 0 && (
                <Button onClick={startCreating}>
                  <Plus className="w-4 h-4 mr-2" />
                  Schedule Meeting
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          filteredMeetings.map((meeting) => (
            <Card key={meeting.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium">{meeting.title}</h3>
                      <Badge className={getStatusColor(meeting.status)}>
                        {getStatusIcon(meeting.status)}
                        <span className="ml-1 capitalize">{meeting.status}</span>
                      </Badge>
                      <Badge variant="outline" className="capitalize">
                        {meeting.platform.replace('_', ' ')}
                      </Badge>
                    </div>
                    
                    {meeting.description && (
                      <p className="text-gray-600 mb-2">{meeting.description}</p>
                    )}
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4" />
                        <span>
                          {new Date(meeting.scheduled_start).toLocaleString()}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4" />
                        <span>{meeting.participants.length} participants</span>
                      </div>
                      
                      {meeting.duration_minutes && (
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4" />
                          <span>{meeting.duration_minutes} minutes</span>
                        </div>
                      )}
                      
                      <div className="flex items-center space-x-2">
                        {meeting.enable_transcription ? (
                          <Mic className="w-4 h-4" />
                        ) : (
                          <MicOff className="w-4 h-4" />
                        )}
                        <span>
                          {meeting.enable_transcription ? 'Transcription enabled' : 'No transcription'}
                        </span>
                      </div>
                    </div>
                    
                    {meeting.participants.length > 0 && (
                      <div className="mt-2">
                        <span className="text-sm text-gray-500">Participants: </span>
                        <span className="text-sm">{meeting.participants.join(', ')}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {meeting.status === 'scheduled' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleStartMeeting(meeting.id)}
                      >
                        <Play className="w-4 h-4" />
                      </Button>
                    )}
                    
                    {meeting.status === 'active' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEndMeeting(meeting.id)}
                      >
                        <Square className="w-4 h-4" />
                      </Button>
                    )}
                    
                    {meeting.status === 'completed' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => fetchTranscript(meeting.id)}
                      >
                        <FileText className="w-4 h-4" />
                      </Button>
                    )}
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startEditing(meeting)}
                      disabled={meeting.status === 'active' || editingMeeting || showCreateForm}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteMeeting(meeting.id)}
                      disabled={meeting.status === 'active' || editingMeeting || showCreateForm}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

