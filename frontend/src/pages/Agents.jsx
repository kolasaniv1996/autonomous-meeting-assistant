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
import { Trash2, Plus, Save, Play, Pause, Settings, BarChart3 } from 'lucide-react';

const Agents = () => {
  const { token } = useAuth();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingAgent, setEditingAgent] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'inactive',
    config_data: {
      jira_username: '',
      github_username: '',
      confluence_username: '',
      meeting_platforms: [],
      capabilities: [],
      max_concurrent_meetings: 1,
      auto_join: false,
      transcription_enabled: true
    }
  });

  const API_BASE = 'http://localhost:8080/api';

  const statusColors = {
    active: 'bg-green-500',
    inactive: 'bg-gray-500',
    busy: 'bg-yellow-500',
    error: 'bg-red-500'
  };

  const capabilities = [
    'Meeting Transcription',
    'Action Item Extraction',
    'Jira Integration',
    'GitHub Integration',
    'Confluence Integration',
    'Meeting Summarization',
    'Automated Responses'
  ];

  const platforms = ['Microsoft Teams', 'Google Meet', 'Zoom', 'Webex'];

  useEffect(() => {
    fetchAgents();
  }, []);

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
        setAgents(data.agents);
      } else {
        setError('Failed to fetch agents');
      }
    } catch (error) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const url = editingAgent 
        ? `${API_BASE}/agents/${editingAgent.id}`
        : `${API_BASE}/agents`;
      
      const method = editingAgent ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setSuccess(editingAgent ? 'Agent updated successfully' : 'Agent created successfully');
        setShowForm(false);
        setEditingAgent(null);
        resetForm();
        fetchAgents();
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to save agent');
      }
    } catch (error) {
      setError('Network error occurred');
    }
  };

  const handleDelete = async (agentId) => {
    if (!confirm('Are you sure you want to delete this agent?')) return;

    try {
      const response = await fetch(`${API_BASE}/agents/${agentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setSuccess('Agent deleted successfully');
        fetchAgents();
      } else {
        setError('Failed to delete agent');
      }
    } catch (error) {
      setError('Network error occurred');
    }
  };

  const handleStatusChange = async (agentId, newStatus) => {
    try {
      const agent = agents.find(a => a.id === agentId);
      const updatedAgent = { ...agent, status: newStatus };

      const response = await fetch(`${API_BASE}/agents/${agentId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedAgent),
      });

      if (response.ok) {
        setSuccess(`Agent ${newStatus === 'active' ? 'activated' : 'deactivated'} successfully`);
        fetchAgents();
      } else {
        setError('Failed to update agent status');
      }
    } catch (error) {
      setError('Network error occurred');
    }
  };

  const handleEdit = (agent) => {
    setEditingAgent(agent);
    const configData = typeof agent.config_data === 'string' 
      ? JSON.parse(agent.config_data) 
      : agent.config_data || {};
    
    setFormData({
      name: agent.name,
      description: agent.description || '',
      status: agent.status,
      config_data: {
        jira_username: configData.jira_username || '',
        github_username: configData.github_username || '',
        confluence_username: configData.confluence_username || '',
        meeting_platforms: configData.meeting_platforms || [],
        capabilities: configData.capabilities || [],
        max_concurrent_meetings: configData.max_concurrent_meetings || 1,
        auto_join: configData.auto_join || false,
        transcription_enabled: configData.transcription_enabled || true
      }
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      status: 'inactive',
      config_data: {
        jira_username: '',
        github_username: '',
        confluence_username: '',
        meeting_platforms: [],
        capabilities: [],
        max_concurrent_meetings: 1,
        auto_join: false,
        transcription_enabled: true
      }
    });
  };

  const handleConfigChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      config_data: {
        ...prev.config_data,
        [field]: value
      }
    }));
  };

  const toggleCapability = (capability) => {
    const currentCapabilities = formData.config_data.capabilities;
    const newCapabilities = currentCapabilities.includes(capability)
      ? currentCapabilities.filter(c => c !== capability)
      : [...currentCapabilities, capability];
    
    handleConfigChange('capabilities', newCapabilities);
  };

  const togglePlatform = (platform) => {
    const currentPlatforms = formData.config_data.meeting_platforms;
    const newPlatforms = currentPlatforms.includes(platform)
      ? currentPlatforms.filter(p => p !== platform)
      : [...currentPlatforms, platform];
    
    handleConfigChange('meeting_platforms', newPlatforms);
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
        <h1 className="text-3xl font-bold">Agents</h1>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Agent
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
              {editingAgent ? 'Edit Agent' : 'New Agent'}
            </CardTitle>
            <CardDescription>
              Configure an autonomous agent for meeting participation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Agent Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Meeting Assistant Bot"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={formData.status} onValueChange={(value) => setFormData(prev => ({ ...prev, status: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="inactive">Inactive</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="busy">Busy</SelectItem>
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
                  placeholder="Describe the agent's purpose and responsibilities"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Jira Username</Label>
                  <Input
                    value={formData.config_data.jira_username}
                    onChange={(e) => handleConfigChange('jira_username', e.target.value)}
                    placeholder="jira.username"
                  />
                </div>
                <div className="space-y-2">
                  <Label>GitHub Username</Label>
                  <Input
                    value={formData.config_data.github_username}
                    onChange={(e) => handleConfigChange('github_username', e.target.value)}
                    placeholder="github-username"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Confluence Username</Label>
                  <Input
                    value={formData.config_data.confluence_username}
                    onChange={(e) => handleConfigChange('confluence_username', e.target.value)}
                    placeholder="confluence.username"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Meeting Platforms</Label>
                <div className="flex flex-wrap gap-2">
                  {platforms.map((platform) => (
                    <Button
                      key={platform}
                      type="button"
                      variant={formData.config_data.meeting_platforms.includes(platform) ? "default" : "outline"}
                      size="sm"
                      onClick={() => togglePlatform(platform)}
                    >
                      {platform}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label>Capabilities</Label>
                <div className="flex flex-wrap gap-2">
                  {capabilities.map((capability) => (
                    <Button
                      key={capability}
                      type="button"
                      variant={formData.config_data.capabilities.includes(capability) ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggleCapability(capability)}
                    >
                      {capability}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max_meetings">Max Concurrent Meetings</Label>
                <Input
                  id="max_meetings"
                  type="number"
                  min="1"
                  max="10"
                  value={formData.config_data.max_concurrent_meetings}
                  onChange={(e) => handleConfigChange('max_concurrent_meetings', parseInt(e.target.value))}
                />
              </div>

              <div className="flex gap-2">
                <Button type="submit">
                  <Save className="w-4 h-4 mr-2" />
                  {editingAgent ? 'Update' : 'Create'} Agent
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowForm(false);
                    setEditingAgent(null);
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
        {agents.map((agent) => {
          const configData = typeof agent.config_data === 'string' 
            ? JSON.parse(agent.config_data) 
            : agent.config_data || {};

          return (
            <Card key={agent.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${statusColors[agent.status]}`}></div>
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {agent.name}
                        <Badge variant="outline">{agent.status}</Badge>
                      </CardTitle>
                      <CardDescription>{agent.description}</CardDescription>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {agent.status === 'active' ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleStatusChange(agent.id, 'inactive')}
                      >
                        <Pause className="w-4 h-4" />
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleStatusChange(agent.id, 'active')}
                      >
                        <Play className="w-4 h-4" />
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(agent)}
                    >
                      <Settings className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(agent.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                  <div>
                    <strong>Platforms:</strong>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {(configData.meeting_platforms || []).map((platform) => (
                        <Badge key={platform} variant="secondary" className="text-xs">
                          {platform}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <strong>Capabilities:</strong>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {(configData.capabilities || []).slice(0, 2).map((capability) => (
                        <Badge key={capability} variant="secondary" className="text-xs">
                          {capability}
                        </Badge>
                      ))}
                      {(configData.capabilities || []).length > 2 && (
                        <Badge variant="secondary" className="text-xs">
                          +{(configData.capabilities || []).length - 2} more
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div>
                    <strong>Max Meetings:</strong> {configData.max_concurrent_meetings || 1}
                  </div>
                  <div>
                    <strong>Created:</strong> {new Date(agent.created_at).toLocaleDateString()}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {agents.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-muted-foreground">No agents found. Create your first agent to get started.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Agents;

