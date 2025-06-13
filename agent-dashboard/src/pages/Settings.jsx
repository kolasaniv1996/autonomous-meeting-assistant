import React, { useState, useEffect } from 'react';
import { fetchWithAuth } from '../utils/api';
import { useAuth } from '../context/AuthContext'; // Optional: if currentUser is stored in context
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

export function Settings() {
  const { currentUser: contextUser } = useAuth(); // Get user from context if available
  const [userData, setUserData] = useState(contextUser || null);
  const [loading, setLoading] = useState(!contextUser); // Only load if not in context
  const [error, setError] = useState(null);

  useEffect(() => {
    // If user data isn't already available from context, fetch it
    if (!contextUser) {
      const fetchUserData = async () => {
        setLoading(true);
        setError(null);
        try {
          const response = await fetchWithAuth('/me');
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.msg || `HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          setUserData(data); // Assuming backend returns user object directly
        } catch (e) {
          console.error("Failed to fetch user data:", e);
          setError(e.message);
        } finally {
          setLoading(false);
        }
      };
      fetchUserData();
    }
  }, [contextUser]); // Re-run if contextUser changes (e.g., after login)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Settings</h2>
        <p className="text-gray-600">Manage your account details and application settings.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Account Details</CardTitle>
          <CardDescription>View your current account information.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading && <p>Loading user data...</p>}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {userData && !loading && !error && (
            <>
              <div>
                <Label htmlFor="username">Username</Label>
                <Input id="username" value={userData.username || ''} readOnly disabled />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" value={userData.email || ''} readOnly disabled />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>Update your account password.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Password change functionality coming soon...</p>
          {/* Placeholder for password change form */}
          {/*
          <form className="space-y-4">
            <div>
              <Label htmlFor="currentPassword">Current Password</Label>
              <Input id="currentPassword" type="password" />
            </div>
            <div>
              <Label htmlFor="newPassword">New Password</Label>
              <Input id="newPassword" type="password" />
            </div>
            <div>
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input id="confirmPassword" type="password" />
            </div>
            <Button type="submit" disabled>Save New Password</Button>
          </form>
          */}
        </CardContent>
      </Card>
    </div>
  );
}

