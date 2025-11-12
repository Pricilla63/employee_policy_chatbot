// import React, { useState } from 'react';
// import { useNavigate, Link } from 'react-router-dom';
// import { authAPI } from '../../services/api';
// import { MessageSquare, Loader2 } from 'lucide-react';
// import * as utils from '../utils/helpers.js';

// const Register = () => {
//   const [formData, setFormData] = useState({
//     email: '',
//     username: '',
//     password: '',
//   });
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);
//   const navigate = useNavigate();

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError('');
//     setLoading(true);

//     try {
//       await authAPI.register(formData);
//       alert('Registration successful! Please login.');
//       navigate('/login');
//     } catch (err) {
//       setError(err.response?.data?.detail || 'Registration failed');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
//       <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
//         <div className="flex items-center justify-center mb-8">
//           <MessageSquare className="w-12 h-12 text-blue-600 mr-3" />
//           <h1 className="text-3xl font-bold text-gray-800">LoanDNA AI</h1>
//         </div>

//         <h2 className="text-2xl font-semibold text-gray-700 mb-6 text-center">
//           Create Account
//         </h2>

//         {error && (
//           <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
//             {error}
//           </div>
//         )}

//         <form onSubmit={handleSubmit} className="space-y-4">
//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">
//               Email
//             </label>
//             <input
//               type="email"
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
//               value={formData.email}
//               onChange={(e) =>
//                 setFormData({ ...formData, email: e.target.value })
//               }
//               required
//               autoFocus
//             />
//           </div>

//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">
//               Username
//             </label>
//             <input
//               type="text"
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
//               value={formData.username}
//               onChange={(e) =>
//                 setFormData({ ...formData, username: e.target.value })
//               }
//               required
//             />
//           </div>

//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-2">
//               Password
//             </label>
//             <input
//               type="password"
//               className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
//               value={formData.password}
//               onChange={(e) =>
//                 setFormData({ ...formData, password: e.target.value })
//               }
//               required
//             />
//           </div>

//           <button
//             type="submit"
//             disabled={loading}
//             className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
//           >
//             {loading ? (
//               <>
//                 <Loader2 className="animate-spin mr-2" size={20} />
//                 Creating account...
//               </>
//             ) : (
//               'Sign Up'
//             )}
//           </button>
//         </form>

//         <p className="mt-6 text-center text-gray-600">
//           Already have an account?{' '}
//           <Link
//             to="/login"
//             className="text-blue-600 hover:text-blue-700 font-semibold"
//           >
//             Sign In
//           </Link>
//         </p>
//       </div>
//     </div>
//   );
// };

// export default Register;




import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../services/api';
import { MessageSquare, Loader2, Check, Eye, EyeOff } from 'lucide-react';
import { isValidEmail, truncateText, copyToClipboard, formatDate } from '../../utils/helpers.js';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [registrationTime] = useState(new Date().toISOString());
  const navigate = useNavigate();

  // Enhanced validation using utils
  const validateForm = () => {
    // Clear previous errors
    setError('');

    // Email validation
    if (!formData.email.trim()) {
      setError('Email is required');
      return false;
    }
    
    if (!isValidEmail(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    
    // Username validation
    if (!formData.username.trim()) {
      setError('Username is required');
      return false;
    }
    
    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters long');
      return false;
    }
    
    // Password validation
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }
    
    if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
      setError('Password should contain both letters and numbers');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setCopied(false);

    try {
      // Call registration API
      const response = await authAPI.register(formData);
      
      // Generate and copy referral code
      const referralCode = `LOANDNA-${formData.username.toUpperCase()}-${Date.now().toString().slice(-6)}`;
      const copySuccess = await copyToClipboard(referralCode);
      
      if (copySuccess) {
        setCopied(true);
      }
      
      // Show success message with referral info
      setTimeout(() => {
        alert(`Registration successful! ${copySuccess ? 'Your referral code has been copied to clipboard.' : 'Please note your referral code.'}\n\nReferral Code: ${referralCode}`);
        navigate('/login');
      }, 500);
      
    } catch (err) {
      // Use truncateText for error messages
      const errorMessage = truncateText(
        err.response?.data?.detail || 
        err.message || 
        'Registration failed. Please check your connection and try again.', 
        120
      );
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (error) {
      setError('');
    }
  };

  // Format username display with truncation if needed
  const displayUsername = formData.username.length > 15 
    ? truncateText(formData.username, 15) 
    : formData.username;

  // Password strength indicator
  const getPasswordStrength = () => {
    if (formData.password.length === 0) return { strength: 0, text: '', color: 'gray' };
    if (formData.password.length < 6) return { strength: 33, text: 'Weak', color: 'red' };
    if (formData.password.length < 8 || !/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
      return { strength: 66, text: 'Medium', color: 'yellow' };
    }
    return { strength: 100, text: 'Strong', color: 'green' };
  };

  const passwordStrength = getPasswordStrength();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-center mb-8">
          <MessageSquare className="w-12 h-12 text-blue-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-800">LoanDNA AI</h1>
        </div>

        <h2 className="text-2xl font-semibold text-gray-700 mb-2 text-center">
          Create Account
        </h2>

        {/* Registration time info */}
        <div className="text-sm text-gray-500 text-center mb-6">
          Ready to join {formatDate(registrationTime).toLowerCase()}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Success Copy Indicator */}
        {copied && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6 transition-all duration-300">
            <div className="flex items-center justify-center">
              <Check size={16} className="mr-2" />
              <span className="text-sm">Referral code copied to clipboard!</span>
            </div>
          </div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Email Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition placeholder-gray-400"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              required
              autoFocus
              placeholder="your.email@example.com"
            />
            {formData.email && !isValidEmail(formData.email) && (
              <p className="text-red-500 text-xs mt-1">Please enter a valid email address</p>
            )}
          </div>

          {/* Username Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition placeholder-gray-400"
              value={formData.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              required
              minLength={3}
              maxLength={20}
              placeholder="Choose a unique username"
            />
            <div className="flex justify-between items-center mt-1">
              <div className="text-xs text-gray-500">
                {formData.username ? (
                  <>
                    Display: <span className="font-medium">{displayUsername}</span>
                    {formData.username.length > 15 && '...'}
                  </>
                ) : (
                  '3-20 characters'
                )}
              </div>
              <div className="text-xs text-gray-500">
                {formData.username.length}/20
              </div>
            </div>
          </div>

          {/* Password Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition placeholder-gray-400 pr-12"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                required
                minLength={6}
                placeholder="At least 6 characters with letters & numbers"
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            
            {/* Password Strength Indicator */}
            {formData.password && (
              <div className="mt-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-gray-500">Password strength</span>
                  <span className={`text-xs font-medium ${
                    passwordStrength.color === 'red' ? 'text-red-500' :
                    passwordStrength.color === 'yellow' ? 'text-yellow-500' :
                    'text-green-500'
                  }`}>
                    {passwordStrength.text}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      passwordStrength.color === 'red' ? 'bg-red-500' :
                      passwordStrength.color === 'yellow' ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${passwordStrength.strength}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg transform hover:scale-[1.02] active:scale-[0.98] transition-transform"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin mr-2" size={20} />
                Creating your account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Login Link */}
        <p className="mt-6 text-center text-gray-600">
          Already have an account?{' '}
          <Link
            to="/login"
            className="text-blue-600 hover:text-blue-700 font-semibold transition-colors"
          >
            Sign in here
          </Link>
        </p>

        {/* Additional Info */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            By creating an account, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;