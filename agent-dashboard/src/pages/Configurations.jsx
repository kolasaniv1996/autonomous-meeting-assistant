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
  Settings, 
  Search,
  Filter,
  CheckCircle,
  AlertCircle,
  Database,
  Cloud,
  Mic
} from 'lucide-react'

const API_BASE_URL = 'http://localhost:5001/api'

export function Configurations() {
  const [configurations, setConfigurations] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingConfig, setEditingConfig] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    config_data: {}
  })
  const [template, setTemplate] = useState(null)

  useEffect(() => {
    fetchConfigurations()
    fetchTemplate()
  }, [])

  const fetchConfigurations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/configurations`)
      const data = await response.json()
      if (data.success) {
        setConfigurations(data.data)
      }
    } catch (error) {
      console.error('Error fetching configurations:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTemplate = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/configurations/template')
      const data = await response.json()
      if (data.success) {
        setTemplate(data.data)
      }
    } catch (error) {
      console.error('Error fetching template:', error)
    }
  }

  const handleCreateConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/configurations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      const data = await response.json()
      if (data.success) {
        setConfigurations([...configurations, data.data])
        setShowCreateForm(false)
        setFormData({ name: '', description: '', config_data: {} })
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error creating configuration:', error)
    }
  }

  const handleUpdateConfig = async (configId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/configurations/${configId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      const data = await response.json()
      if (data.success) {
        setConfigurations(configurations.map(config => 
          config.id === configId ? data.data : config
        ))
        setEditingConfig(null)
        setFormData({ name: '', description: '', config_data: {} })
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error updating configuration:', error)
    }
  }

  const handleDeleteConfig = async (configId) => {
    if (!confirm('Are you sure you want to delete this configuration?')) return
    
    try {
      const response = await fetch(`${API_BASE_URL}/configurations/${configId}`, {
        method: 'DELETE',
      })
      const data = await response.json()
      if (data.success) {
        setConfigurations(configurations.filter(config => config.id !== configId))
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error deleting configuration:', error)
    }
  }

  const handleActivateConfig = async (configId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/configurations/${configId}/activate`, {method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: true }),
      })
      const data = await response.json()
      if (data.success) {
        setConfigurations(configurations.map(config => ({
          ...config,
          is_active: config.id === configId
        })))
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error activating configuration:', error)
    }
  }

  const startEditing = (config) => {
    setEditingConfig(config.id)
    setFormData({
      name: config.name,
      description: config.description || '',
      config_data: config.config_data
    })
  }

  const startCreating = () => {
    setShowCreateForm(true)
    setFormData({
      name: '',
      description: '',
      config_data: template || {}
    })
  }

  const cancelEditing = () => {
    setEditingConfig(null)
    setShowCreateForm(false)
    setFormData({ name: '', description: '', config_data: {} })
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Configurations</h2>
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
          <h2 className="text-2xl font-bold">Configurations</h2>
          <p className="text-gray-600">Manage your agent framework configurations</p>
        </div>
        <Button onClick={startCreating} disabled={showCreateForm || editingConfig}>
          <Plus className="w-4 h-4 mr-2" />
          New Configuration
        </Button>
      </div>

      {/* Create/Edit Form */}
      {(showCreateForm || editingConfig) && (
        <Card>
          <CardHeader>
            <CardTitle>
              {showCreateForm ? 'Create New Configuration' : 'Edit Configuration'}
            </CardTitle>
            <CardDescription>
              {showCreateForm 
                ? 'Set up a new configuration for your agents'
                : 'Modify the selected configuration'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="basic" className="space-y-4">
              <TabsList>
                <TabsTrigger value="basic">Basic Info</TabsTrigger>
                <TabsTrigger value="api">API Credentials</TabsTrigger>
                <TabsTrigger value="platforms">Meeting Platforms</TabsTrigger>
                <TabsTrigger value="speech">Speech Processing</TabsTrigger>
                <TabsTrigger value="employees">Employees</TabsTrigger>
              </TabsList>

              <TabsContent value="basic" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Configuration Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      placeholder="e.g., Production Config"
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      placeholder="Brief description of this configuration"
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="api" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="jira_url">Jira URL</Label>
                    <Input
                      id="jira_url"
                      value={formData.config_data?.api_credentials?.jira_url || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        config_data: {
                          ...formData.config_data,
                          api_credentials: {
                            ...formData.config_data.api_credentials,
                            jira_url: e.target.value
                          }
                        }
                      })}
                      placeholder="https://your-company.atlassian.net"
                    />
                  </div>
                  <div>
                    <Label htmlFor="jira_token">Jira API Token</Label>
                    <Input
                      id="jira_token"
                      type="password"
                      value={formData.config_data?.api_credentials?.jira_token || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        config_data: {
                          ...formData.config_data,
                          api_credentials: {
                            ...formData.config_data.api_credentials,
                            jira_token: e.target.value
                          }
                        }
                      })}
                      placeholder="Your Jira API token"
                    />
                  </div>
                  <div>
                    <Label htmlFor="github_token">GitHub Token</Label>
                    <Input
                      id="github_token"
                      type="password"
                      value={formData.config_data?.api_credentials?.github_token || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        config_data: {
                          ...formData.config_data,
                          api_credentials: {
                            ...formData.config_data.api_credentials,
                            github_token: e.target.value
                          }
                        }
                      })}
                      placeholder="Your GitHub personal access token"
                    />
                  </div>
                  <div>
                    <Label htmlFor="openai_key">OpenAI API Key</Label>
                    <Input
                      id="openai_key"
                      type="password"
                      value={formData.config_data?.api_credentials?.openai_api_key || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        config_data: {
                          ...formData.config_data,
                          api_credentials: {
                            ...formData.config_data.api_credentials,
                            openai_api_key: e.target.value
                          }
                        }
                      })}
                      placeholder="Your OpenAI API key"
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="platforms" className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <Label>Preferred Platform</Label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={formData.config_data?.meeting_platforms?.preferred_platform || 'teams'}
                      onChange={(e) => setFormData({
                        ...formData,
                        config_data: {
                          ...formData.config_data,
                          meeting_platforms: {
                            ...formData.config_data.meeting_platforms,
                            preferred_platform: e.target.value
                          }
                        }
                      })}
                    >
                      <option value="teams">Microsoft Teams</option>
                      <option value="google_meet">Google Meet</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="teams_app_id">Teams App ID</Label>
                      <Input
                        id="teams_app_id"
                        value={formData.config_data?.api_credentials?.teams_app_id || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          config_data: {
                            ...formData.config_data,
                            api_credentials: {
                              ...formData.config_data.api_credentials,
                              teams_app_id: e.target.value
                            }
                          }
                        })}
                        placeholder="Microsoft Teams App ID"
                      />
                    </div>
                    <div>
                      <Label htmlFor="teams_app_password">Teams App Password</Label>
                      <Input
                        id="teams_app_password"
                        type="password"
                        value={formData.config_data?.api_credentials?.teams_app_password || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          config_data: {
                            ...formData.config_data,
                            api_credentials: {
                              ...formData.config_data.api_credentials,
                              teams_app_password: e.target.value
                            }
                          }
                        })}
                        placeholder="Microsoft Teams App Password"
                      />
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="speech" className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <Label>Preferred Speech Provider</Label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={formData.config_data?.speech_processing?.preferred_provider || 'azure'}
                      onChange={(e) => setFormData({
                        ...formData,
                        config_data: {
                          ...formData.config_data,
                          speech_processing: {
                            ...formData.config_data.speech_processing,
                            preferred_provider: e.target.value
                          }
                        }
                      })}
                    >
                      <option value="azure">Azure Speech Services</option>
                      <option value="google_cloud">Google Cloud Speech</option>
                      <option value="whisper">OpenAI Whisper</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="azure_speech_key">Azure Speech Key</Label>
                      <Input
                        id="azure_speech_key"
                        type="password"
                        value={formData.config_data?.api_credentials?.azure_speech_key || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          config_data: {
                            ...formData.config_data,
                            api_credentials: {
                              ...formData.config_data.api_credentials,
                              azure_speech_key: e.target.value
                            }
                          }
                        })}
                        placeholder="Azure Speech Services key"
                      />
                    </div>
                    <div>
                      <Label htmlFor="azure_speech_region">Azure Speech Region</Label>
                      <Input
                        id="azure_speech_region"
                        value={formData.config_data?.api_credentials?.azure_speech_region || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          config_data: {
                            ...formData.config_data,
                            api_credentials: {
                              ...formData.config_data.api_credentials,
                              azure_speech_region: e.target.value
                            }
                          }
                        })}
                        placeholder="e.g., eastus"
                      />
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="employees" className="space-y-4">
                <div>
                  <Label>Employee Configuration (JSON)</Label>
                  <Textarea
                    className="h-40 font-mono text-sm"
                    value={JSON.stringify(formData.config_data?.employees || {}, null, 2)}
                    onChange={(e) => {
                      try {
                        const employees = JSON.parse(e.target.value)
                        setFormData({
                          ...formData,
                          config_data: {
                            ...formData.config_data,
                            employees
                          }
                        })
                      } catch (error) {
                        // Invalid JSON, don't update
                      }
                    }}
                    placeholder="Employee configuration in JSON format"
                  />
                </div>
              </TabsContent>
            </Tabs>

            <div className="flex justify-end space-x-2 pt-4 border-t">
              <Button variant="outline" onClick={cancelEditing}>
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button 
                onClick={() => showCreateForm ? handleCreateConfig() : handleUpdateConfig(editingConfig)}
              >
                <Save className="w-4 h-4 mr-2" />
                {showCreateForm ? 'Create' : 'Save'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Configurations List */}
      <div className="grid gap-4">
        {configurations.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No configurations found</h3>
              <p className="text-gray-500 mb-4">Get started by creating your first configuration</p>
              <Button onClick={startCreating}>
                <Plus className="w-4 h-4 mr-2" />
                Create Configuration
              </Button>
            </CardContent>
          </Card>
        ) : (
          configurations.map((config) => (
            <Card key={config.id} className={config.is_active ? 'ring-2 ring-blue-500' : ''}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-medium">{config.name}</h3>
                      {config.is_active && (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Active
                        </Badge>
                      )}
                    </div>
                    {config.description && (
                      <p className="text-gray-600 mt-1">{config.description}</p>
                    )}
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                      <span>Created: {new Date(config.created_at).toLocaleDateString()}</span>
                      <span>Updated: {new Date(config.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {!config.is_active && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleActivateConfig(config.id)}
                      >
                        <Settings className="w-4 h-4 mr-1" />
                        Activate
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startEditing(config)}
                      disabled={editingConfig || showCreateForm}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteConfig(config.id)}
                      disabled={config.is_active || editingConfig || showCreateForm}
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

