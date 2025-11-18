import React, { useState } from 'react';
import bankingService from '../services/bankingService';
import authService from '../services/authService';

const ApiTester = () => {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});

  const testEndpoint = async (endpointName, testFunction) => {
    setLoading(prev => ({ ...prev, [endpointName]: true }));
    
    try {
      const result = await testFunction();
      setResults(prev => ({ 
        ...prev, 
        [endpointName]: { success: true, data: result } 
      }));
    } catch (error) {
      setResults(prev => ({ 
        ...prev, 
        [endpointName]: { success: false, error: error.message } 
      }));
    } finally {
      setLoading(prev => ({ ...prev, [endpointName]: false }));
    }
  };

  const tests = [
    {
      name: 'Auth Test',
      key: 'authTest',
      test: () => authService.testAuth()
    },
    {
      name: 'Connected User Test',
      key: 'connectedUser',
      test: () => bankingService.testConnectedUser()
    },
    {
      name: 'Get All Users',
      key: 'allUsers',
      test: () => bankingService.getAllUsers()
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">API Connection Tester</h2>
      <div className="space-y-4">
        {tests.map(test => (
          <div key={test.key} className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium">{test.name}</h3>
              <button
                onClick={() => testEndpoint(test.key, test.test)}
                disabled={loading[test.key]}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading[test.key] ? 'Testing...' : 'Test'}
              </button>
            </div>
            
            {results[test.key] && (
              <div className={`p-3 rounded-md text-sm ${
                results[test.key].success 
                  ? 'bg-green-50 text-green-800 border border-green-200' 
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}>
                <div className="font-medium mb-1">
                  {results[test.key].success ? 'Success' : 'Error'}
                </div>
                <pre className="text-xs overflow-auto max-h-40">
                  {JSON.stringify(
                    results[test.key].success 
                      ? results[test.key].data 
                      : results[test.key].error, 
                    null, 2
                  )}
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ApiTester;