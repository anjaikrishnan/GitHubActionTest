const http = require('http');

const options = {
  hostname: 'localhost',
  port: 4000,
  path: '/cubejs-api/v1/meta',
  method: 'GET',
  timeout: 5000
};

const req = http.request(options, (res) => {
  if (res.statusCode === 200) {
    console.log('Analytics service is healthy');
    process.exit(0);
  } else {
    console.log(`Analytics service returned status code: ${res.statusCode}`);
    process.exit(1);
  }
});

req.on('error', (err) => {
  console.log(`Health check failed: ${err.message}`);
  process.exit(1);
});

req.on('timeout', () => {
  console.log('Health check timed out');
  req.destroy();
  process.exit(1);
});

req.setTimeout(5000);
req.end();