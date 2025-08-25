import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const requestCount = new Counter('request_count');

// Test configuration
export const options = {
  stages: [
    // Ramp up
    { duration: '2m', target: 10 },   // Ramp up to 10 users over 2 minutes
    { duration: '5m', target: 10 },   // Stay at 10 users for 5 minutes
    { duration: '2m', target: 50 },   // Ramp up to 50 users over 2 minutes
    { duration: '5m', target: 50 },   // Stay at 50 users for 5 minutes
    { duration: '2m', target: 100 },  // Ramp up to 100 users over 2 minutes
    { duration: '5m', target: 100 },  // Stay at 100 users for 5 minutes
    { duration: '2m', target: 0 },    // Ramp down to 0 users over 2 minutes
  ],
  thresholds: {
    // Performance thresholds
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
    http_req_failed: ['rate<0.05'],    // Error rate should be below 5%
    error_rate: ['rate<0.05'],         // Custom error rate should be below 5%
    response_time: ['p(95)<2000'],     // 95% of response times should be below 2s
  },
};

// Base URLs for services
const BASE_URLS = {
  users: 'https://users-staging-278319877545.southamerica-east1.run.app',
  content: 'https://content-staging-278319877545.southamerica-east1.run.app',
  health: 'https://health-check-staging-278319877545.southamerica-east1.run.app',
  backend: 'https://backend-staging-278319877545.southamerica-east1.run.app',
  plans: 'https://plans-service-staging-278319877545.southamerica-east1.run.app',
  tracking: 'https://tracking-service-staging-278319877545.southamerica-east1.run.app'
};

// Test data
const testUsers = [
  { email: 'loadtest1@evolveyou.com.br', password: 'LoadTest123!' },
  { email: 'loadtest2@evolveyou.com.br', password: 'LoadTest123!' },
  { email: 'loadtest3@evolveyou.com.br', password: 'LoadTest123!' },
  { email: 'loadtest4@evolveyou.com.br', password: 'LoadTest123!' },
  { email: 'loadtest5@evolveyou.com.br', password: 'LoadTest123!' },
];

export function setup() {
  console.log('Setting up load test...');
  
  // Create test users if they don't exist
  const createdUsers = [];
  
  for (const user of testUsers) {
    const registerResponse = http.post(`${BASE_URLS.users}/auth/register`, JSON.stringify({
      email: user.email,
      password: user.password,
      full_name: `Load Test User ${user.email}`,
      date_of_birth: '1990-01-01',
      gender: 'masculino'
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (registerResponse.status === 201 || registerResponse.status === 409) {
      // User created or already exists
      createdUsers.push(user);
    }
  }
  
  console.log(`Setup complete. ${createdUsers.length} test users ready.`);
  return { users: createdUsers };
}

export default function(data) {
  const user = data.users[Math.floor(Math.random() * data.users.length)];
  
  // Test scenario selection (weighted)
  const scenario = Math.random();
  
  if (scenario < 0.3) {
    // 30% - Health check scenario
    healthCheckScenario();
  } else if (scenario < 0.6) {
    // 30% - User authentication scenario
    userAuthScenario(user);
  } else if (scenario < 0.8) {
    // 20% - Content browsing scenario
    contentBrowsingScenario();
  } else {
    // 20% - Full user flow scenario
    fullUserFlowScenario(user);
  }
  
  sleep(1); // Wait 1 second between iterations
}

function healthCheckScenario() {
  const group = 'Health Check Scenario';
  
  // Test all health endpoints
  for (const [service, url] of Object.entries(BASE_URLS)) {
    const startTime = Date.now();
    const response = http.get(`${url}/health`, {
      timeout: '30s',
      tags: { name: `${service}_health`, group: group }
    });
    
    const duration = Date.now() - startTime;
    responseTime.add(duration);
    requestCount.add(1);
    
    const success = check(response, {
      [`${service} health check status is 200`]: (r) => r.status === 200,
      [`${service} health check response time < 2s`]: () => duration < 2000,
      [`${service} health check has status field`]: (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.hasOwnProperty('status');
        } catch {
          return false;
        }
      }
    });
    
    errorRate.add(!success);
  }
}

function userAuthScenario(user) {
  const group = 'User Authentication Scenario';
  
  // Login
  const startTime = Date.now();
  const loginResponse = http.post(`${BASE_URLS.users}/auth/login`, JSON.stringify({
    email: user.email,
    password: user.password
  }), {
    headers: { 'Content-Type': 'application/json' },
    timeout: '30s',
    tags: { name: 'user_login', group: group }
  });
  
  const loginDuration = Date.now() - startTime;
  responseTime.add(loginDuration);
  requestCount.add(1);
  
  const loginSuccess = check(loginResponse, {
    'Login status is 200': (r) => r.status === 200,
    'Login response time < 3s': () => loginDuration < 3000,
    'Login returns access token': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.tokens && body.tokens.access_token;
      } catch {
        return false;
      }
    }
  });
  
  errorRate.add(!loginSuccess);
  
  if (loginSuccess && loginResponse.status === 200) {
    try {
      const loginData = JSON.parse(loginResponse.body);
      const accessToken = loginData.tokens.access_token;
      
      // Get user profile
      const profileStartTime = Date.now();
      const profileResponse = http.get(`${BASE_URLS.users}/users/me`, {
        headers: { 
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        timeout: '30s',
        tags: { name: 'user_profile', group: group }
      });
      
      const profileDuration = Date.now() - profileStartTime;
      responseTime.add(profileDuration);
      requestCount.add(1);
      
      const profileSuccess = check(profileResponse, {
        'Profile status is 200': (r) => r.status === 200,
        'Profile response time < 2s': () => profileDuration < 2000,
        'Profile returns user data': (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.email === user.email;
          } catch {
            return false;
          }
        }
      });
      
      errorRate.add(!profileSuccess);
      
    } catch (e) {
      console.error('Error in user auth scenario:', e);
      errorRate.add(true);
    }
  }
}

function contentBrowsingScenario() {
  const group = 'Content Browsing Scenario';
  
  // Browse exercises
  const exercisesStartTime = Date.now();
  const exercisesResponse = http.get(`${BASE_URLS.content}/exercises?limit=20`, {
    timeout: '30s',
    tags: { name: 'browse_exercises', group: group }
  });
  
  const exercisesDuration = Date.now() - exercisesStartTime;
  responseTime.add(exercisesDuration);
  requestCount.add(1);
  
  const exercisesSuccess = check(exercisesResponse, {
    'Exercises status is 200': (r) => r.status === 200,
    'Exercises response time < 2s': () => exercisesDuration < 2000,
    'Exercises returns array': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body);
      } catch {
        return false;
      }
    }
  });
  
  errorRate.add(!exercisesSuccess);
  
  // Browse foods
  const foodsStartTime = Date.now();
  const foodsResponse = http.get(`${BASE_URLS.content}/foods?search=arroz&limit=10`, {
    timeout: '30s',
    tags: { name: 'browse_foods', group: group }
  });
  
  const foodsDuration = Date.now() - foodsStartTime;
  responseTime.add(foodsDuration);
  requestCount.add(1);
  
  const foodsSuccess = check(foodsResponse, {
    'Foods status is 200': (r) => r.status === 200,
    'Foods response time < 2s': () => foodsDuration < 2000,
    'Foods returns array': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body);
      } catch {
        return false;
      }
    }
  });
  
  errorRate.add(!foodsSuccess);
}

function fullUserFlowScenario(user) {
  const group = 'Full User Flow Scenario';
  
  // 1. Login
  const loginResponse = http.post(`${BASE_URLS.users}/auth/login`, JSON.stringify({
    email: user.email,
    password: user.password
  }), {
    headers: { 'Content-Type': 'application/json' },
    timeout: '30s',
    tags: { name: 'full_flow_login', group: group }
  });
  
  requestCount.add(1);
  
  if (loginResponse.status !== 200) {
    errorRate.add(true);
    return;
  }
  
  let accessToken;
  try {
    const loginData = JSON.parse(loginResponse.body);
    accessToken = loginData.tokens.access_token;
  } catch {
    errorRate.add(true);
    return;
  }
  
  const headers = {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  };
  
  // 2. Get user profile
  const profileResponse = http.get(`${BASE_URLS.users}/users/me`, {
    headers: headers,
    timeout: '30s',
    tags: { name: 'full_flow_profile', group: group }
  });
  
  requestCount.add(1);
  errorRate.add(profileResponse.status !== 200);
  
  // 3. Browse content
  const contentResponse = http.get(`${BASE_URLS.content}/exercises?limit=5`, {
    timeout: '30s',
    tags: { name: 'full_flow_content', group: group }
  });
  
  requestCount.add(1);
  errorRate.add(contentResponse.status !== 200);
  
  // 4. Check tracking data (if available)
  const trackingResponse = http.get(`${BASE_URLS.tracking}/progress`, {
    headers: headers,
    timeout: '30s',
    tags: { name: 'full_flow_tracking', group: group }
  });
  
  requestCount.add(1);
  // Tracking might return 404 if no data, which is acceptable
  errorRate.add(trackingResponse.status >= 500);
  
  // Overall flow success check
  const flowSuccess = check(null, {
    'Full flow completed successfully': () => 
      loginResponse.status === 200 && 
      profileResponse.status === 200 && 
      contentResponse.status === 200
  });
  
  if (!flowSuccess) {
    errorRate.add(true);
  }
}

export function teardown(data) {
  console.log('Load test completed.');
  console.log(`Total test users used: ${data.users.length}`);
}

export function handleSummary(data) {
  return {
    'load-test-results.json': JSON.stringify(data, null, 2),
    'load-test-summary.html': `
<!DOCTYPE html>
<html>
<head>
    <title>EvolveYou Load Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
        .success { background: #d4edda; }
        .warning { background: #fff3cd; }
        .error { background: #f8d7da; }
    </style>
</head>
<body>
    <h1>EvolveYou Load Test Results</h1>
    <div class="metric">
        <h3>Test Duration</h3>
        <p>${Math.round(data.state.testRunDurationMs / 1000)}s</p>
    </div>
    <div class="metric">
        <h3>Total Requests</h3>
        <p>${data.metrics.http_reqs.count}</p>
    </div>
    <div class="metric ${data.metrics.http_req_failed.rate < 0.05 ? 'success' : 'error'}">
        <h3>Error Rate</h3>
        <p>${(data.metrics.http_req_failed.rate * 100).toFixed(2)}%</p>
    </div>
    <div class="metric ${data.metrics.http_req_duration.p95 < 2000 ? 'success' : 'warning'}">
        <h3>Response Time (95th percentile)</h3>
        <p>${data.metrics.http_req_duration.p95.toFixed(2)}ms</p>
    </div>
    <div class="metric">
        <h3>Average Response Time</h3>
        <p>${data.metrics.http_req_duration.avg.toFixed(2)}ms</p>
    </div>
    <div class="metric">
        <h3>Max Response Time</h3>
        <p>${data.metrics.http_req_duration.max.toFixed(2)}ms</p>
    </div>
</body>
</html>
    `
  };
}

