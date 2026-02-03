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
    <div className="glass-card rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 text-glass">API Connection Tester</h2>
      <div className="space-y-4">
        {tests.map(test => (
          <div key={test.key} className="border border-white/10 rounded-xl p-4 bg-slate-900/50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-glass">{test.name}</h3>
              <button
                onClick={() => testEndpoint(test.key, test.test)}
                disabled={loading[test.key]}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                {loading[test.key] ? 'Testing...' : 'Test'}
              </button>
            </div>

            {results[test.key] && (
              <div className={`p-3 rounded-lg text-sm border ${results[test.key].success
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-red-500/10 text-red-400 border-red-500/20'
                }`}>
                <div className="font-medium mb-1">
                  {results[test.key].success ? 'Success' : 'Error'}
                </div>
                <pre className="text-xs overflow-auto max-h-40 text-glass-muted">
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