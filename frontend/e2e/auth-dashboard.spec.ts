import { test, expect } from '@playwright/test';

const TEST_EMAIL = 'test@example.com';
const TEST_PASSWORD = 'TestPass123';

test.describe('Sign in and dashboard', () => {
  test('sign in with test user and see dashboard', async ({ page }) => {
    await page.goto('/signin');

    await page.getByPlaceholder(/email/i).fill(TEST_EMAIL);
    await page.getByPlaceholder(/password/i).fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/dashboard|\/$/);
    await expect(page.getByRole('heading', { name: /research opportunities/i })).toBeVisible({ timeout: 10000 });
  });
});
