import { test, expect } from '@playwright/test';

test('Simple Canvas dashboard test', async ({ page }) => {
  // Navigate to the dashboard
  await page.goto('/');
  
  // Wait for page to load
  await page.waitForLoadState('networkidle');
  
  // Check that we're on the right page
  await expect(page.locator('h1')).toContainText('Canvas AI Labs');
  
  // Take a screenshot to see what's happening
  await page.screenshot({ 
    path: 'test-artifacts/dashboard-state.png',
    fullPage: true 
  });
  
  // Test the proxy directly
  const response = await page.request.get('/api/health');
  expect(response.status()).toBe(200);
  const health = await response.json();
  expect(health.status).toBe('ok');
  
  console.log('✅ Basic dashboard and proxy test passed!');
});