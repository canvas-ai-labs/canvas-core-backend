import { test, expect } from '@playwright/test';

interface MetricsResponse {
  courses: number;
  assignments: number;
  deadlines: number;
  scheduled_jobs: number;
}

test('Canvas sync E2E workflow', async ({ page }) => {
  // Navigate to the dashboard
  await page.goto('/');

  // Wait for page to load
  await page.waitForLoadState('networkidle');

  // Check that we're on the right page
  await expect(page.locator('h1')).toContainText('Canvas AI Labs');

  // Wait for page to stabilize and clear any initial errors
  await page.waitForTimeout(3000);

  // Try to dismiss any error banners by clicking retry if they exist
  const retryButton = page.locator('button:has-text("Retry")');
  const retryCount = await retryButton.count();
  if (retryCount > 0) {
    console.log('Found retry buttons, clicking them to clear errors');
    for (let i = 0; i < retryCount; i++) {
      await retryButton.nth(i).click();
      await page.waitForTimeout(1000);
    }
  }

  // Take screenshot before sync
  await page.screenshot({ 
    path: 'test-artifacts/before-sync.png',
    fullPage: true 
  });

  // Find and click the Full Sync button
  const fullSyncButton = page.locator('button:has-text("Full Sync")');
  await expect(fullSyncButton).toBeVisible();
  await fullSyncButton.click();

  console.log('Clicked Full Sync button, waiting for sync to complete...');

  // Poll the backend directly to check if sync worked
  let courses = 0;
  let attempts = 0;
  const maxAttempts = 30; // 30 seconds with 1 second intervals

  while (courses === 0 && attempts < maxAttempts) {
    try {
      // Use the proxy to call the backend
      const response = await page.request.get('/api/metrics');
      if (response.ok()) {
        const metrics: MetricsResponse = await response.json();
        courses = metrics.courses;
        console.log(`Attempt ${attempts + 1}: Found ${courses} courses`);
        
        if (courses > 0) {
          break;
        }
      }
    } catch (error) {
      console.log(`Attempt ${attempts + 1}: Error fetching metrics:`, error);
    }
    
    attempts++;
    await page.waitForTimeout(1000); // Wait 1 second between attempts
  }

  // Assert that we found courses
  expect(courses).toBeGreaterThan(0);
  console.log(`✅ Sync completed! Found ${courses} courses.`);

  // Wait for UI to update
  await page.waitForTimeout(3000);

  // Take final screenshot
  await page.screenshot({ 
    path: 'test-artifacts/canvas-sync.png',
    fullPage: true 
  });

  console.log(`✅ E2E test completed successfully! Found ${courses} courses after sync.`);
});