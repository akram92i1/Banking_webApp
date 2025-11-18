// Quick test script - paste this in browser console when on http://localhost:3000
// Make sure backend is running on port 8082

console.log('🧪 Testing Login API directly...');

// Test 1: Check if backend is reachable
fetch('http://localhost:8082/api/auth/test')
  .then(response => response.text())
  .then(data => {
    console.log('✅ Backend reachable:', data);
    
    // Test 2: Try login with sample credentials
    return fetch('http://localhost:8082/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        identifier: 'test@example.com',  // Change this to your actual test user
        password: 'password123'         // Change this to your actual test password
      })
    });
  })
  .then(response => {
    console.log('Login response status:', response.status);
    return response.text();
  })
  .then(responseText => {
    console.log('Login raw response:', responseText);
    try {
      const data = JSON.parse(responseText);
      console.log('Login parsed response:', data);
      
      if (data.token) {
        console.log('✅ Login successful! Token received:', data.token.substring(0, 20) + '...');
      } else {
        console.log('❌ No token in response');
      }
    } catch (e) {
      console.log('❌ Response is not valid JSON:', responseText);
    }
  })
  .catch(error => {
    console.error('❌ Login test failed:', error);
  });

console.log('📝 Check the logs above. If you see CORS errors, the backend might not be running.');
console.log('📝 If you see 403/401 errors, check if you have valid user credentials in the database.');
console.log('📝 If you see JSON parsing errors, there might be an issue with the response format.');