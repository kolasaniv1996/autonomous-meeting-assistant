import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Trash2, Plus, Save, Download, Upload } from 'lucide-react';

const Configuration = () => {
  const { token } = useAuth();
  const [configurations, setConfigurations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  const [formData, setFormData] = useState({
    config_name: '',
    config_data: {
      jira: { url: '', username: '', token: '' },
      github: { token: '', username: '' },
      confluence: { url: '', username: '', token: '' },
      teams: { tenant_id: '', client_id: '', client_secret: '' },
      azure_speech: { subscription_key: '', region: '' },
      google_cloud: { project_id: '', credentials_json: '' }
    },
    is_active: false
  });

  const API_BASE = 'http://localhost:8080/api';

  useEffect(() => {
    fetchConfigurations();
  }, []);

  const fetchConfigurations = async () => {
    try {
      const response = await fetch(`${API_BASE}/configurations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setConfigurations(data.configurations);
      } else {
        setError('Failed to fetch configurations');
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
      const url = editingConfig 
        ? `${API_BASE}/configurations/${editingConfig.id}`
        : `${API_BASE}/configurations`;
      
      const method = editingConfig ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setSuccess(editingConfig ? 'Configuration updated successfully' : 'Configuration created successfully');
        setShowForm(false);
        setEditingConfig(null);
        resetForm();
        fetchConfigurations();
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to save configuration');
      }
    } catch (error) {
      setError('Network error occurred');
    }
  };

  const handleDelete = async (configId) => {
    if (!confirm('Are you sure you want to delete this configuration?')) return;

    try {
      const response = await fetch(`${API_BASE}/configurations/${configId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setSuccess('Configuration deleted successfully');
        fetchConfigurations();
      } else {
        setError('Failed to delete configuration');
      }
    } catch (error) {
      setError('Network error occurred');
    }
  };

  const handleEdit = (config) => {
    setEditingConfig(config);
    setFormData({
      config_name: config.config_name,
      config_data: typeof config.config_data === 'string' 
        ? JSON.parse(config.config_data) 
        : config.config_data,
      is_active: config.is_active
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      config_name: '',
      config_data: {
        jira: { url: '', username: '', token: '' },
        github: { token: '', username: '' },
        confluence: { url: '', username: '', token: '' },
        teams: { tenant_id: '', client_id: '', client_secret: '' },
        azure_speech: { subscription_key: '', region: '' },
        google_cloud: { project_id: '', credentials_json: '' }
      },
      is_active: false
    });
  };

  const handleConfigDataChange = (service, field, value) => {
    setFormData(prev => ({
      ...prev,
      config_data: {
        ...prev.config_data,
        [service]: {
          ...prev.config_data[service],
          [field]: value
        }
      }
    }));
  };

  const exportConfiguration = (config) => {
    const dataStr = JSON.stringify(config, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `config_${config.config_name}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const importConfiguration = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const config = JSON.parse(e.target.result);
          setFormData({
            config_name: config.config_name || '',
            config_data: config.config_data || formData.config_data,
            is_active: false
          });
          setShowForm(true);
        } catch (error) {
          setError('Invalid configuration file');
        }
      };
      reader.readAsText(file);
    }
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
        <h1 className="text-3xl font-bold">Configurations</h1>
        <div className="flex gap-2">
          <input
            type="file"
            accept=".json"
            onChange={importConfiguration}
            className="hidden"
            id="import-config"
          />
          <Button
            variant="outline"
            onClick={() => document.getElementById('import-config').click()}
          >
            <Upload className="w-4 h-4 mr-2" />
            Import
          </Button>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Configuration
          </Button>
        </div>
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
              {editingConfig ? 'Edit Configuration' : 'New Configuration'}
            </CardTitle>
            <CardDescription>
              Configure API credentials and settings for various services
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="config_name">Configuration Name</Label>
                <Input
                  id="config_name"
                  value={formData.config_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, config_name: e.target.value }))}
                  placeholder="e.g., Production Config"
                  required
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_active: checked }))}
                />
                <Label htmlFor="is_active">Set as Active Configuration</Label>
              </div>

              {/* Jira Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Jira Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Jira URL</Label>
                      <Input
                        value={formData.config_data.jira.url}
                        onChange={(e) => handleConfigDataChange('jira', 'url', e.target.value)}
                        placeholder="https://your-domain.atlassian.net"
                      />
                    </div>
                    <div>
                      <Label>Username</Label>
                      <Input
                        value={formData.config_data.jira.username}
                        onChange={(e) => handleConfigDataChange('jira', 'username', e.target.value)}
                        placeholder="your-email@example.com"
                      />
                    </div>
                  </div>
                  <div>
                    <Label>API Token</Label>
                    <Input
                      type="password"
                      value={formData.config_data.jira.token}
                      onChange={(e) => handleConfigDataChange('jira', 'token', e.target.value)}
                      placeholder="Your Jira API token"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* GitHub Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">GitHub Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Username</Label>
                      <Input
                        value={formData.config_data.github.username}
                        onChange={(e) => handleConfigDataChange('github', 'username', e.target.value)}
                        placeholder="your-github-username"
                      />
                    </div>
                    <div>
                      <Label>Personal Access Token</Label>
                      <Input
                        type="password"
                        value={formData.config_data.github.token}
                        onChange={(e) => handleConfigDataChange('github', 'token', e.target.value)}
                        placeholder="ghp_xxxxxxxxxxxx"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Teams Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Microsoft Teams Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label>Tenant ID</Label>
                      <Input
                        value={formData.config_data.teams.tenant_id}
                        onChange={(e) => handleConfigDataChange('teams', 'tenant_id', e.target.value)}
                        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                      />
                    </div>
                    <div>
                      <Label>Client ID</Label>
                      <Input
                        value={formData.config_data.teams.client_id}
                        onChange={(e) => handleConfigDataChange('teams', 'client_id', e.target.value)}
                        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                      />
                    </div>
                    <div>
                      <Label>Client Secret</Label>
                      <Input
                        type="password"
                        value={formData.config_data.teams.client_secret}
                        onChange={(e) => handleConfigDataChange('teams', 'client_secret', e.target.value)}
                        placeholder="Your client secret"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Azure Speech Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Azure Speech Services</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Subscription Key</Label>
                      <Input
                        type="password"
                        value={formData.config_data.azure_speech.subscription_key}
                        onChange={(e) => handleConfigDataChange('azure_speech', 'subscription_key', e.target.value)}
                        placeholder="Your Azure Speech subscription key"
                      />
                    </div>
                    <div>
                      <Label>Region</Label>
                      <Input
                        value={formData.config_data.azure_speech.region}
                        onChange={(e) => handleConfigDataChange('azure_speech', 'region', e.target.value)}
                        placeholder="e.g., eastus"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="flex gap-2">
                <Button type="submit">
                  <Save className="w-4 h-4 mr-2" />
                  {editingConfig ? 'Update' : 'Create'} Configuration
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowForm(false);
                    setEditingConfig(null);
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
        {configurations.map((config) => (
          <Card key={config.id} className={config.is_active ? 'border-primary' : ''}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    {config.config_name}
                    {config.is_active && (
                      <span className="bg-primary text-primary-foreground text-xs px-2 py-1 rounded">
                        Active
                      </span>
                    )}
                  </CardTitle>
                  <CardDescription>
                    Created: {new Date(config.created_at).toLocaleDateString()}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => exportConfiguration(config)}
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(config)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDelete(config.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>

      {configurations.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-muted-foreground">No configurations found. Create your first configuration to get started.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Configuration;

