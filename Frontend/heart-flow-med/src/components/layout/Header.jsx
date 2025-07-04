import { Bell, Search, User, LogOut, Settings } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import useUserProfile from '../../hooks/useUserProfile';
import { Link } from 'react-router-dom';

const Header = () => {
  const { user, logout } = useAuth();
  const { profile, loading, error } = useUserProfile();

  const getRoleSpecificInfo = () => {
    if (!profile) return null;

    switch (profile.role) {
      case 'Cardiologist':
        return (
          <div className="text-xs text-gray-500">
            {profile.specialization} • {profile.experience} years
          </div>
        );
      case 'Nurse':
        return (
          <div className="text-xs text-gray-500">
            {profile.department}
          </div>
        );
      case 'Administrative Staff':
        return (
          <div className="text-xs text-gray-500">
            {profile.office_location}
          </div>
        );
      case 'Patient':
        return (
          <div className="text-xs text-gray-500">
            ID: {profile.unique_id}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Search Bar */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Search patients, appointments..."
              />
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="p-2 text-gray-400 hover:text-gray-600 relative">
              <Bell className="h-6 w-6" />
              <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
            </button>

            {/* User Menu */}
            <div className="relative">
              <div className="flex items-center space-x-3">
                <Link to="/profile" className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                    <User className="h-5 w-5 text-white" />
                  </div>
                </Link>
                <Link to="/profile" className="hidden md:block">
                  <div className="text-sm font-medium text-gray-900">
                    {profile?.first_name || user?.first_name} {profile?.last_name || user?.last_name}
                  </div>
                  {loading ? (
                    <div className="text-xs text-gray-500">Loading...</div>
                  ) : error ? (
                    <div className="text-xs text-red-500">{error}</div>
                  ) : (
                    getRoleSpecificInfo()
                  )}
                </Link>
                <div className="flex items-center space-x-2">
                  <Link to="/profile" className="p-1 text-gray-400 hover:text-gray-600">
                    <Settings className="h-5 w-5" />
                  </Link>
                  <button
                    onClick={logout}
                    className="p-1 text-gray-400 hover:text-red-600"
                  >
                    <LogOut className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 