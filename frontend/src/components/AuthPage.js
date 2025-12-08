import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner';
import { Shield, MapPin, Users, CheckCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://trafsafe.preview.emergentagent.com';
const API = `${BACKEND_URL}/api`;

export default function AuthPage({ onLogin, onGuestLogin }) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    company_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [showReset, setShowReset] = useState(false);

  const [resetData, setResetData] = useState({
    email: '',
    new_password: '',
    confirm_password: ''
  });

  const handleResetChange = (e) => {
    setResetData({ ...resetData, [e.target.name]: e.target.value });
  };

  const handlePasswordReset = async () => {
    if (!resetData.email || !resetData.new_password || !resetData.confirm_password) {
      toast.error('Please enter email, new password and confirm password');
      return;
    }

    if (resetData.new_password !== resetData.confirm_password) {
      toast.error('New password and confirm password do not match');
      return;
    }

    try {
      const response = await fetch(`${API}/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: resetData.email,
          new_password: resetData.new_password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      toast.success('Password reset successfully. You can now sign in with your new password.');
      setShowReset(false);
      setFormData((prev) => ({ ...prev, email: resetData.email, password: '' }));
      setResetData({ email: '', new_password: '', confirm_password: '' });
    } catch (error) {
      console.error('Password reset error:', error);
      toast.error(error.message || 'Failed to reset password. Please try again.');
    }
  };



  const handleSubmit = async (isLogin) => {
    console.log('=== FORM SUBMISSION STARTED ===');
    console.log('Is Login:', isLogin);
    console.log('Form Data:', { email: formData.email, company: formData.company_name });
    
    setLoading(true);
    
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin ? 
        { email: formData.email, password: formData.password } :
        formData;

      const url = `${API}${endpoint}`;
      console.log('Submitting to:', url);
      console.log('Payload:', { ...payload, password: '***' }); // Hide password in logs

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
        console.error('API Error Response:', errorData);
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ API Success - Response received');
      console.log('Has token:', !!data.token);
      console.log('Has user:', !!data.user);
      console.log('User data:', data.user);
      
      // Validate response structure
      if (!data.token || !data.user) {
        console.error('❌ Invalid response structure:', data);
        throw new Error('Invalid response format from server - missing token or user data');
      }
      
      // Show success message first
      const successMessage = isLogin ? 'Welcome back!' : 'Account created successfully!';
      toast.success(successMessage);
      
      console.log('Calling onLogin...');
      
      // Call onLogin with proper data
      onLogin(data.token, data.user);
      
      console.log('✅ onLogin called successfully');
      
    } catch (error) {
      console.error('❌ Authentication error:', error);
      console.error('Error type:', error.constructor.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      
      const errorMessage = error.message || 'Authentication failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
      console.log('=== FORM SUBMISSION COMPLETE ===');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-orange-50 to-amber-50">
      {/* Hero Section */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-orange-600/10 to-amber-600/10"></div>
        <div className="relative container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto text-center mb-16">
            <div className="flex justify-center items-center mb-8">
              <div className="p-4 bg-orange-500 rounded-full shadow-lg">
                <Shield className="w-12 h-12 text-white" />
              </div>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-slate-800 mb-6 font-serif">
              SafeRoad<span className="text-orange-600">Works</span>
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto leading-relaxed">
              Create professional Austroads-approved traffic management plans with interactive mapping and comprehensive device positioning
            </p>
            <div className="flex flex-wrap justify-center gap-8 text-slate-700">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>DTMR Compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-5 h-5 text-orange-600" />
                <span>Interactive Maps</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-600" />
                <span>Team Collaboration</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 pb-16">
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="text-center p-8 bg-white rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-amber-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <MapPin className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-slate-800 mb-3">Interactive Planning</h3>
            <p className="text-slate-600">Position traffic control devices on Google Maps with precision and real-time feedback</p>
          </div>
          <div className="text-center p-8 bg-white rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-white" />
              {showReset && (
                <div className="mb-6 p-4 border border-orange-200 rounded-lg bg-orange-50">
                  <h3 className="text-sm font-semibold text-slate-800 mb-2">Reset your password</h3>
                  <div className="space-y-3">
                    <div className="space-y-1">
                      <Label htmlFor="reset_email">Email</Label>
                      <Input
                        id="reset_email"
                        name="email"
                        type="email"
                        placeholder="Enter your email"
                        value={resetData.email}
                        onChange={handleResetChange}
                        className="h-10"
                      />
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="reset_password">New Password</Label>
                      <Input
                        id="reset_password"
                        name="new_password"
                        type="password"
                        placeholder="Enter new password"
                        value={resetData.new_password}
                        onChange={handleResetChange}
                        className="h-10"
                      />
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="reset_confirm_password">Confirm Password</Label>
                      <Input
                        id="reset_confirm_password"
                        name="confirm_password"
                        type="password"
                        placeholder="Confirm new password"
                        value={resetData.confirm_password}
                        onChange={handleResetChange}
                        className="h-10"
                      />
                    </div>
                    <div className="flex items-center justify-end gap-2 pt-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setShowReset(false)}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        className="bg-orange-500 hover:bg-orange-600 text-white"
                        onClick={handlePasswordReset}
                      >
                        Save New Password
                      </Button>
                    </div>
                  </div>
                </div>
              )}


            </div>
            <h3 className="text-xl font-semibold text-slate-800 mb-3">Compliance Ready</h3>
            <p className="text-slate-600">Generate professional PDF reports that meet all Austroads and DTMR requirements</p>
          </div>
          <div className="text-center p-8 bg-white rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-slate-800 mb-3">Team Management</h3>
            <p className="text-slate-600">Save and share plans across your organization with secure user accounts</p>
          </div>
        </div>

        {/* Auth Form */}
        <div className="max-w-md mx-auto">
          <Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl font-bold text-slate-800">Get Started</CardTitle>
              <CardDescription className="text-slate-600">
                Join thousands of professionals using SafeRoadWorks
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Guest Mode Button - Always Visible at Top */}
              {onGuestLogin && (
                <div className="mb-6">
                  <Button 
                    onClick={onGuestLogin}
                    className="w-full h-12 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-bold text-lg shadow-lg"
                  >
                    🚀 Try Demo Now (No Login Required)
                  </Button>
                  <p className="text-center text-xs text-slate-500 mt-2">
                    Test all features instantly without creating an account
                  </p>
                  <div className="relative my-6">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t border-slate-300" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                      <span className="bg-white px-2 text-slate-500">Or sign in with your account</span>
                    </div>
                  </div>
                </div>
              )}
              
              <Tabs defaultValue="login" className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-6">
                  <TabsTrigger value="login">Sign In</TabsTrigger>
                  <TabsTrigger value="register">Create Account</TabsTrigger>
                </TabsList>
                
                <TabsContent value="login" className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="Enter your email"
                      value={formData.email}
                      onChange={handleChange}
                      className="h-11"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={handleChange}
                      className="h-11"
                    />
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-600 mb-2">
                    <button
                      type="button"
                      onClick={() => setShowReset(true)}
                      className="text-orange-600 hover:underline"
                    >
                      Forgot password?
                    </button>
                  </div>

                  <Button 
                    onClick={() => handleSubmit(true)}
                    disabled={loading}
                    className="w-full h-11 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-semibold"
                  >
                    {loading ? 'Signing In...' : 'Sign In'}
                  </Button>
                  
                  {/* Guest Mode Button for Testing */}
                  {onGuestLogin && (
                    <Button 
                      onClick={onGuestLogin}
                      variant="outline"
                      className="w-full h-11 border-2 border-blue-300 text-blue-700 hover:bg-blue-50 font-semibold mt-3"
                    >
                      🚀 Continue as Guest (Demo Mode)
                    </Button>
                  )}
                </TabsContent>
                
                <TabsContent value="register" className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="company_name">Company Name</Label>
                    <Input
                      id="company_name"
                      name="company_name"
                      placeholder="Your company name"
                      value={formData.company_name}
                      onChange={handleChange}
                      className="h-11"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="Enter your email"
                      value={formData.email}
                      onChange={handleChange}
                      className="h-11"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      placeholder="Create a password"
                      value={formData.password}
                      onChange={handleChange}
                      className="h-11"
                    />
                  </div>
                  <Button 
                    onClick={() => handleSubmit(false)}
                    disabled={loading}
                    className="w-full h-11 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-semibold"
                  >
                    {loading ? 'Creating Account...' : 'Create Account'}
                  </Button>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}