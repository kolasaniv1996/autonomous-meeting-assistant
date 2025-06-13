import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Plus, 
  Edit, 
  Trash2, 
  Save, 
  X, 
  Users, 
  Search,
  Filter,
  UserCheck,
  UserX,
  Mail,
  Briefcase,
  Github,
  FileText
} from 'lucide-react'

import { API_BASE_URL } from '../utils/api'

export function Agents() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingAgent, setEditingAgent] = useState(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterTeam, setFilterTeam] = useState('')
  const [filterProject, setFilterProject] = useState('')
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    email: '',
    role: '',
    teams: [],
    projects: [],
    jira_username: '',
    github_username: '',
    confluence_username: '',
    is_active: true
  })
  const [stats, setStats] = useState({})

  useEffect(() => {
    fetchAgents()
    fetchStats()
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/agents`)
      const data = await response.json()
      if (data.success) {
        setAgents(data.data)
      }
    } catch (error) {
      console.error('Error fetching agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/agents/stats')
      const data = await response.json()
      if (data.success) {
        setStats(data.data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleCreateAgent = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      const data = await response.json()
      if (data.success) {
        setAgents([...agents, data.data])
        setShowCreateForm(false)
        resetForm()
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error creating agent:', error)
    }
  }

  const handleUpdateAgent = async (agentId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/agents/${agentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      const data = await response.json()
      if (data.success) {
        setAgents(agents.map(agent => 
          agent.id === agentId ? data.data : agent
        ))
        setEditingAgent(null)
        resetForm()
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error updating agent:', error)
    }
  }

  const handleDeleteAgent = async (agentId) => {
    if (!confirm('Are you sure you want to delete this agent?')) return
    
    try {
      const response = await fetch(`http://localhost:5000/api/agents/${agentId}`, {
        method: 'DELETE',
      })
      const data = await response.json()
      if (data.success) {
        setAgents(agents.filter(agent => agent.id !== agentId))
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error deleting agent:', error)
    }
  }

  const handleToggleStatus = async (agentId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/agents/${agentId}/toggle`, {
        method: 'POST',
      })
      const data = await response.json()
      if (data.success) {
        setAgents(agents.map(agent => 
          agent.id === agentId ? data.data : agent
        ))
        fetchStats()
      } else {
        alert(data.error)
      }
    } catch (error) {
      console.error('Error toggling agent status:', error)
    }
  }

  const startEditing = (agent) => {
    setEditingAgent(agent.id)
    setFormData({
      employee_id: agent.employee_id,
      name: agent.name,
      email: agent.email,
      role: agent.role || '',
      teams: agent.teams || [],
      projects: agent.projects || [],
      jira_username: agent.jira_username || '',
      github_username: agent.github_username || '',
      confluence_username: agent.confluence_username || '',
      is_active: agent.is_active
    })
  }

  const startCreating = () => {
    setShowCreateForm(true)
    resetForm()
  }

  const resetForm = () => {
    setFormData({
      employee_id: '',
      name: '',
      email: '',
      role: '',
      teams: [],
      projects: [],
      jira_username: '',
      github_username: '',
      confluence_username: '',
      is_active: true
    })
  }

  const cancelEditing = () => {
    setEditingAgent(null)
    setShowCreateForm(false)
    resetForm()
  }

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.employee_id.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesTeam = !filterTeam || agent.teams.includes(filterTeam)
    const matchesProject = !filterProject || agent.projects.includes(filterProject)
    
    return matchesSearch && matchesTeam && matchesProject
  })

  const allTeams = [...new Set(agents.flatMap(agent => agent.teams || []))]
  const allProjects = [...new Set(agents.flatMap(agent => agent.projects || []))]

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Agents</h2>
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
          <h2 className="text-2xl font-bold">Agents</h2>
          <p className="text-gray-600">Manage your autonomous agents</p>
        </div>
        <Button onClick={startCreating} disabled={showCreateForm || editingAgent}>
          <Plus className="w-4 h-4 mr-2" />
          New Agent
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Agents</p>
                <p className="text-2xl font-bold">{stats.total_agents || 0}</p>
              </div>
              <Users className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Agents</p>
                <p className="text-2xl font-bold text-green-600">{stats.active_agents || 0}</p>
              </div>
              <UserCheck className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Inactive Agents</p>
                <p className="text-2xl font-bold text-red-600">{stats.inactive_agents || 0}</p>
              </div>
              <UserX className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Teams</p>
                <p className="text-2xl font-bold">{allTeams.length}</p>
              </div>
              <Briefcase className="w-8 h-8 text-purple-500" />
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
                  placeholder="Search agents by name, email, or ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <select
                className="px-3 py-2 border rounded-md"
                value={filterTeam}
                onChange={(e) => setFilterTeam(e.target.value)}
              >
                <option value="">All Teams</option>
                {allTeams.map(team => (
                  <option key={team} value={team}>{team}</option>
                ))}
              </select>
              <select
                className="px-3 py-2 border rounded-md"
                value={filterProject}
                onChange={(e) => setFilterProject(e.target.value)}
              >
                <option value="">All Projects</option>
                {allProjects.map(project => (
                  <option key={project} value={project}>{project}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Create/Edit Form */}
      {(showCreateForm || editingAgent) && (
        <Card>
          <CardHeader>
            <CardTitle>
              {showCreateForm ? 'Create New Agent' : 'Edit Agent'}
            </CardTitle>
            <CardDescription>
              {showCreateForm 
                ? 'Set up a new autonomous agent'
                : 'Modify the selected agent'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="employee_id">Employee ID</Label>
                <Input
                  id="employee_id"
                  value={formData.employee_id}
                  onChange={(e) => setFormData({...formData, employee_id: e.target.value})}
                  placeholder="e.g., john.doe"
                />
              </div>
              <div>
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="e.g., John Doe"
                />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="e.g., john.doe@company.com"
                />
              </div>
              <div>
                <Label htmlFor="role">Role</Label>
                <Input
                  id="role"
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  placeholder="e.g., Software Engineer"
                />
              </div>
              <div>
                <Label htmlFor="teams">Teams (comma-separated)</Label>
                <Input
                  id="teams"
                  value={formData.teams.join(', ')}
                  onChange={(e) => setFormData({
                    ...formData, 
                    teams: e.target.value.split(',').map(t => t.trim()).filter(t => t)
                  })}
                  placeholder="e.g., backend-team, api-team"
                />
              </div>
              <div>
                <Label htmlFor="projects">Projects (comma-separated)</Label>
                <Input
                  id="projects"
                  value={formData.projects.join(', ')}
                  onChange={(e) => setFormData({
                    ...formData, 
                    projects: e.target.value.split(',').map(p => p.trim()).filter(p => p)
                  })}
                  placeholder="e.g., PROJECT-A, PROJECT-B"
                />
              </div>
              <div>
                <Label htmlFor="jira_username">Jira Username</Label>
                <Input
                  id="jira_username"
                  value={formData.jira_username}
                  onChange={(e) => setFormData({...formData, jira_username: e.target.value})}
                  placeholder="Jira username"
                />
              </div>
              <div>
                <Label htmlFor="github_username">GitHub Username</Label>
                <Input
                  id="github_username"
                  value={formData.github_username}
                  onChange={(e) => setFormData({...formData, github_username: e.target.value})}
                  placeholder="GitHub username"
                />
              </div>
              <div>
                <Label htmlFor="confluence_username">Confluence Username</Label>
                <Input
                  id="confluence_username"
                  value={formData.confluence_username}
                  onChange={(e) => setFormData({...formData, confluence_username: e.target.value})}
                  placeholder="Confluence username"
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                />
                <Label htmlFor="is_active">Active Agent</Label>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4 border-t mt-4">
              <Button variant="outline" onClick={cancelEditing}>
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button 
                onClick={() => showCreateForm ? handleCreateAgent() : handleUpdateAgent(editingAgent)}
              >
                <Save className="w-4 h-4 mr-2" />
                {showCreateForm ? 'Create' : 'Save'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Agents List */}
      <div className="grid gap-4">
        {filteredAgents.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {agents.length === 0 ? 'No agents found' : 'No agents match your filters'}
              </h3>
              <p className="text-gray-500 mb-4">
                {agents.length === 0 
                  ? 'Get started by creating your first agent'
                  : 'Try adjusting your search or filter criteria'
                }
              </p>
              {agents.length === 0 && (
                <Button onClick={startCreating}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Agent
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          filteredAgents.map((agent) => (
            <Card key={agent.id} className={agent.is_active ? '' : 'opacity-60'}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium">{agent.name}</h3>
                      <Badge variant={agent.is_active ? 'default' : 'secondary'}>
                        {agent.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      {agent.role && (
                        <Badge variant="outline">{agent.role}</Badge>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Mail className="w-4 h-4" />
                        <span>{agent.email}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4" />
                        <span>ID: {agent.employee_id}</span>
                      </div>
                      
                      {agent.teams && agent.teams.length > 0 && (
                        <div className="flex items-center space-x-2">
                          <Briefcase className="w-4 h-4" />
                          <span>Teams: {agent.teams.join(', ')}</span>
                        </div>
                      )}
                      
                      {agent.projects && agent.projects.length > 0 && (
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4" />
                          <span>Projects: {agent.projects.join(', ')}</span>
                        </div>
                      )}
                      
                      {agent.github_username && (
                        <div className="flex items-center space-x-2">
                          <Github className="w-4 h-4" />
                          <span>GitHub: {agent.github_username}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>Created: {new Date(agent.created_at).toLocaleDateString()}</span>
                      <span>Updated: {new Date(agent.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleStatus(agent.id)}
                      disabled={editingAgent || showCreateForm}
                    >
                      {agent.is_active ? (
                        <UserX className="w-4 h-4" />
                      ) : (
                        <UserCheck className="w-4 h-4" />
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startEditing(agent)}
                      disabled={editingAgent || showCreateForm}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteAgent(agent.id)}
                      disabled={editingAgent || showCreateForm}
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

