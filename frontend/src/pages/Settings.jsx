import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Save, Download, Upload, RefreshCw } from 'lucide-react';

const Settings = () => {
  const { token, user } = useAuth();
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);

  const API_BASE = 'http://localhost:8080/api';

  const defaultSettings = {
    // System Settings
    system_timezone: 'UTC',
    system_language: 'en',
    log_level: 'INFO',
    max_concurrent_meetings: 10,
    session_timeout: 3600,
    
    // Notification Settings
    email_notifications: true,
    in_app_notifications: true,
    webhook_notifications: false,
    webhook_url: '',
    notification_frequency: 'immediate',
    
    // Meeting Settings
    default_meeting_duration: 60,
    auto_join_meetings: false,
    enable_transcription: true,
    enable_recording: false,
    meeting_reminder_minutes: 15,
    
    // Integration Settings
    jira_sync_enabled: false,
    github_sync_enabled: false,
    confluence_sync_enabled: false,
    calendar_sync_enabled: false,
    
    // Security Settings
    require_2fa: false,
    password_expiry_days: 90,
    max_login_attempts: 5,
    session_encryption: true,
    
    // API Settings
    rate_limit_requests: 100,
    rate_limit_window: 60,
    api_timeout: 30,
    enable_api_logging: true,
    
    // Backup Settings
    auto_backup_enabled: true,
    backup_frequency: 'daily',
    backup_retention_days: 30,
    backup_location: 'local'
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${API_BASE}/settings`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const settingsObj = {};
        data.settings.forEach(setting => {
          settingsObj[setting.setting_key] = setting.setting_value;
        });
        setSettings({ ...defaultSettings, ...settingsObj });
      } else {
        setSettings(defaultSettings);
      }
    } catch (error) {
      setError('Failed to load settings');
      setSettings(defaultSettings);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_BASE}/settings`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        setSuccess('Settings saved successfully');
      } else {
        setError('Failed to save settings');
      }
    } catch (error) {
      setError('Network error occurred');
    } finally {
      setSaving(false);
    }
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const exportSettings = () => {
    const dataStr = JSON.stringify(settings, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `settings_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const importSettings = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result);
          setSettings({ ...defaultSettings, ...importedSettings });
          setSuccess('Settings imported successfully');
        } catch (error) {
          setError('Invalid settings file');
        }
      };
      reader.readAsText(file);
    }
  };

  const resetToDefaults = () => {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
      setSettings(defaultSettings);
      setSuccess('Settings reset to defaults');
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
        <h1 className="text-3xl font-bold">Settings</h1>
        <div className="flex gap-2">
          <input
            type="file"
            accept=".json"
            onChange={importSettings}
            className="hidden"
            id="import-settings"
          />
          <Button
            variant="outline"
            onClick={() => document.getElementById('import-settings').click()}
          >
            <Upload className="w-4 h-4 mr-2" />
            Import
          </Button>
          <Button variant="outline" onClick={exportSettings}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" onClick={resetToDefaults}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save Settings'}
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

      <Tabs defaultValue="system" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="system">System</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="meetings">Meetings</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="api">API & Backup</TabsTrigger>
        </TabsList>

        <TabsContent value="system">
          <Card>
            <CardHeader>
              <CardTitle>System Settings</CardTitle>
              <CardDescription>Configure system-wide preferences and behavior</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>System Timezone</Label>
                  <Select 
                    value={settings.system_timezone} 
                    onValueChange={(value) => handleSettingChange('system_timezone', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                      <SelectItem value="Europe/London">London</SelectItem>
                      <SelectItem value="Europe/Paris">Paris</SelectItem>
                      <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>System Language</Label>
                  <Select 
                    value={settings.system_language} 
                    onValueChange={(value) => handleSettingChange('system_language', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                      <SelectItem value="ja">Japanese</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Log Level</Label>
                  <Select 
                    value={settings.log_level} 
                    onValueChange={(value) => handleSettingChange('log_level', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="DEBUG">Debug</SelectItem>
                      <SelectItem value="INFO">Info</SelectItem>
                      <SelectItem value="WARNING">Warning</SelectItem>
                      <SelectItem value="ERROR">Error</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Max Concurrent Meetings</Label>
                  <Input
                    type="number"
                    min="1"
                    max="50"
                    value={settings.max_concurrent_meetings}
                    onChange={(e) => handleSettingChange('max_concurrent_meetings', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Session Timeout (seconds)</Label>
                <Input
                  type="number"
                  min="300"
                  max="86400"
                  value={settings.session_timeout}
                  onChange={(e) => handleSettingChange('session_timeout', parseInt(e.target.value))}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
              <CardDescription>Configure how and when you receive notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                  </div>
                  <Switch
                    checked={settings.email_notifications}
                    onCheckedChange={(checked) => handleSettingChange('email_notifications', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>In-App Notifications</Label>
                    <p className="text-sm text-muted-foreground">Show notifications in the application</p>
                  </div>
                  <Switch
                    checked={settings.in_app_notifications}
                    onCheckedChange={(checked) => handleSettingChange('in_app_notifications', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Webhook Notifications</Label>
                    <p className="text-sm text-muted-foreground">Send notifications to external webhooks</p>
                  </div>
                  <Switch
                    checked={settings.webhook_notifications}
                    onCheckedChange={(checked) => handleSettingChange('webhook_notifications', checked)}
                  />
                </div>
              </div>

              {settings.webhook_notifications && (
                <div className="space-y-2">
                  <Label>Webhook URL</Label>
                  <Input
                    value={settings.webhook_url}
                    onChange={(e) => handleSettingChange('webhook_url', e.target.value)}
                    placeholder="https://your-webhook-url.com/notifications"
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label>Notification Frequency</Label>
                <Select 
                  value={settings.notification_frequency} 
                  onValueChange={(value) => handleSettingChange('notification_frequency', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="immediate">Immediate</SelectItem>
                    <SelectItem value="hourly">Hourly Digest</SelectItem>
                    <SelectItem value="daily">Daily Digest</SelectItem>
                    <SelectItem value="weekly">Weekly Digest</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="meetings">
          <Card>
            <CardHeader>
              <CardTitle>Meeting Settings</CardTitle>
              <CardDescription>Configure default meeting behavior and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Default Meeting Duration (minutes)</Label>
                  <Input
                    type="number"
                    min="15"
                    max="480"
                    value={settings.default_meeting_duration}
                    onChange={(e) => handleSettingChange('default_meeting_duration', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Meeting Reminder (minutes before)</Label>
                  <Input
                    type="number"
                    min="0"
                    max="60"
                    value={settings.meeting_reminder_minutes}
                    onChange={(e) => handleSettingChange('meeting_reminder_minutes', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Auto-join Meetings</Label>
                    <p className="text-sm text-muted-foreground">Automatically join scheduled meetings</p>
                  </div>
                  <Switch
                    checked={settings.auto_join_meetings}
                    onCheckedChange={(checked) => handleSettingChange('auto_join_meetings', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Enable Transcription</Label>
                    <p className="text-sm text-muted-foreground">Automatically transcribe meeting audio</p>
                  </div>
                  <Switch
                    checked={settings.enable_transcription}
                    onCheckedChange={(checked) => handleSettingChange('enable_transcription', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Enable Recording</Label>
                    <p className="text-sm text-muted-foreground">Record meetings when possible</p>
                  </div>
                  <Switch
                    checked={settings.enable_recording}
                    onCheckedChange={(checked) => handleSettingChange('enable_recording', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations">
          <Card>
            <CardHeader>
              <CardTitle>Integration Settings</CardTitle>
              <CardDescription>Enable and configure third-party integrations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Jira Sync</Label>
                    <p className="text-sm text-muted-foreground">Sync meeting actions with Jira tickets</p>
                  </div>
                  <Switch
                    checked={settings.jira_sync_enabled}
                    onCheckedChange={(checked) => handleSettingChange('jira_sync_enabled', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>GitHub Sync</Label>
                    <p className="text-sm text-muted-foreground">Create GitHub issues from meeting actions</p>
                  </div>
                  <Switch
                    checked={settings.github_sync_enabled}
                    onCheckedChange={(checked) => handleSettingChange('github_sync_enabled', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Confluence Sync</Label>
                    <p className="text-sm text-muted-foreground">Save meeting notes to Confluence</p>
                  </div>
                  <Switch
                    checked={settings.confluence_sync_enabled}
                    onCheckedChange={(checked) => handleSettingChange('confluence_sync_enabled', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Calendar Sync</Label>
                    <p className="text-sm text-muted-foreground">Sync with external calendars</p>
                  </div>
                  <Switch
                    checked={settings.calendar_sync_enabled}
                    onCheckedChange={(checked) => handleSettingChange('calendar_sync_enabled', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>Configure security and authentication settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Require Two-Factor Authentication</Label>
                    <p className="text-sm text-muted-foreground">Require 2FA for all users</p>
                  </div>
                  <Switch
                    checked={settings.require_2fa}
                    onCheckedChange={(checked) => handleSettingChange('require_2fa', checked)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Session Encryption</Label>
                    <p className="text-sm text-muted-foreground">Encrypt user session data</p>
                  </div>
                  <Switch
                    checked={settings.session_encryption}
                    onCheckedChange={(checked) => handleSettingChange('session_encryption', checked)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Password Expiry (days)</Label>
                  <Input
                    type="number"
                    min="30"
                    max="365"
                    value={settings.password_expiry_days}
                    onChange={(e) => handleSettingChange('password_expiry_days', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Max Login Attempts</Label>
                  <Input
                    type="number"
                    min="3"
                    max="10"
                    value={settings.max_login_attempts}
                    onChange={(e) => handleSettingChange('max_login_attempts', parseInt(e.target.value))}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api">
          <Card>
            <CardHeader>
              <CardTitle>API & Backup Settings</CardTitle>
              <CardDescription>Configure API limits and backup preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Rate Limit (requests)</Label>
                  <Input
                    type="number"
                    min="10"
                    max="1000"
                    value={settings.rate_limit_requests}
                    onChange={(e) => handleSettingChange('rate_limit_requests', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Rate Limit Window (seconds)</Label>
                  <Input
                    type="number"
                    min="60"
                    max="3600"
                    value={settings.rate_limit_window}
                    onChange={(e) => handleSettingChange('rate_limit_window', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>API Timeout (seconds)</Label>
                  <Input
                    type="number"
                    min="5"
                    max="120"
                    value={settings.api_timeout}
                    onChange={(e) => handleSettingChange('api_timeout', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Enable API Logging</Label>
                  <p className="text-sm text-muted-foreground">Log all API requests and responses</p>
                </div>
                <Switch
                  checked={settings.enable_api_logging}
                  onCheckedChange={(checked) => handleSettingChange('enable_api_logging', checked)}
                />
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Auto Backup</Label>
                    <p className="text-sm text-muted-foreground">Automatically backup system data</p>
                  </div>
                  <Switch
                    checked={settings.auto_backup_enabled}
                    onCheckedChange={(checked) => handleSettingChange('auto_backup_enabled', checked)}
                  />
                </div>

                {settings.auto_backup_enabled && (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Backup Frequency</Label>
                        <Select 
                          value={settings.backup_frequency} 
                          onValueChange={(value) => handleSettingChange('backup_frequency', value)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="hourly">Hourly</SelectItem>
                            <SelectItem value="daily">Daily</SelectItem>
                            <SelectItem value="weekly">Weekly</SelectItem>
                            <SelectItem value="monthly">Monthly</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Retention Period (days)</Label>
                        <Input
                          type="number"
                          min="1"
                          max="365"
                          value={settings.backup_retention_days}
                          onChange={(e) => handleSettingChange('backup_retention_days', parseInt(e.target.value))}
                        />
                      </div>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Settings;

