import { test, expect } from '@playwright/test';

test('Debug Canvas sync', async ({ page }) => {
  // Navigate to the dashboard
  await page.goto('/');
  
  // Wait for page to load
  await page.waitForLoadState('networkidle');
  
  // Wait for page to stabilize
  await page.waitForTimeout(3000);
  
  // Take initial screenshot
  await page.screenshot({ 
    path: 'test-artifacts/initial-state.png',
    fullPage: true 
  });
  
  // Click retry buttons if they exist
  const retryButton = page.locator('button:has-text("Retry")');
  const retryCount = await retryButton.count();
  if (retryCount > 0) {
    console.log(`Found ${retryCount} retry buttons, clicking them`);
    for (let i = 0; i < retryCount; i++) {
      await retryButton.nth(i).click();
      await page.waitForTimeout(1000);
    }
  }
  
  // Take screenshot after retry
  await page.screenshot({ 
    path: 'test-artifacts/after-retry.png',
    fullPage: true 
  });
  
  // Find and click the Full Sync button
  const fullSyncButton = page.locator('button:has-text("Full Sync")');
  console.log(`Full Sync button count: ${await fullSyncButton.count()}`);
  
  if (await fullSyncButton.count() > 0) {
    await fullSyncButton.click();
    console.log('Clicked Full Sync button');
    
    // Wait a bit and take another screenshot
    await page.waitForTimeout(3000);
    await page.screenshot({ 
      path: 'test-artifacts/after-sync-click.png',
      fullPage: true 
    });
  }
  
  console.log('✅ Debug test completed!');
});