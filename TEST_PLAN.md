# FitTrack Pro - Testing Plan

Complete testing checklist before launch.

## Pre-Launch Testing

### 1. Local Setup Test

```bash
# Run setup
./setup.sh

# Verify .env created
cat .env

# Add Stripe test keys to .env (see STRIPE_SETUP.md)

# Start app
./start.sh
```

✅ App starts without errors
✅ Accessible at http://localhost:3000

### 2. Landing Page Tests

- ✅ Visit http://localhost:3000
- ✅ Page loads correctly
- ✅ All links work (How It Works, Pricing, Login, Sign Up)
- ✅ "Start Free Trial" button redirects to /signup
- ✅ Responsive on mobile (resize browser)

### 3. Signup Flow Tests

**Test Case 1: Successful Signup**
- ✅ Go to /signup
- ✅ Enter email: `test@example.com`
- ✅ Enter password: `testpass123`
- ✅ Click "Create Account"
- ✅ Redirects to /dashboard
- ✅ User is logged in

**Test Case 2: Duplicate Email**
- ✅ Try signing up again with same email
- ✅ Shows error message

**Test Case 3: Validation**
- ✅ Try empty email - shows error
- ✅ Try invalid email - shows error
- ✅ Try short password - shows error

### 4. Login Flow Tests

**Test Case 1: Successful Login**
- ✅ Logout
- ✅ Go to /login
- ✅ Enter correct credentials
- ✅ Redirects to /dashboard
- ✅ User is logged in

**Test Case 2: Failed Login**
- ✅ Try wrong password - shows error
- ✅ Try non-existent email - shows error

### 5. Dashboard Tests

**Test Case 1: Initial State**
- ✅ Dashboard loads
- ✅ All stats show 0 or default values
- ✅ Charts render (empty but no errors)
- ✅ User email shows in navbar
- ✅ Logout link works

**Test Case 2: Trial Banner**
- ✅ Trial banner shows for new users
- ✅ "Subscribe Now" button works

### 6. Data Logging Tests

**Test Case 1: Log Food**
```bash
# Via curl (while logged in)
curl -X POST http://localhost:3000/api/log-food \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Chicken breast",
    "calories": 200,
    "protein": 40,
    "carbs": 0,
    "fat": 5
  }'
```
- ✅ Food logged successfully
- ✅ Dashboard updates (refresh page)
- ✅ Macros show correctly
- ✅ Progress bars update

**Test Case 2: Log Weight**
```bash
curl -X POST http://localhost:3000/api/log-weight \
  -H "Content-Type: application/json" \
  -d '{"weight": 185}'
```
- ✅ Weight logged successfully
- ✅ Dashboard shows new weight
- ✅ Chart updates

**Test Case 3: Log Workout**
```bash
curl -X POST http://localhost:3000/api/log-workout \
  -H "Content-Type: application/json" \
  -d '{
    "lifts": [
      {"name": "Bench Press", "weight": 225, "reps": 5},
      {"name": "Squat", "weight": 315, "reps": 5}
    ]
  }'
```
- ✅ Workout logged successfully
- ✅ 1RM calculated correctly

### 7. User Data Isolation Test

**Test Case 1: Multiple Users**
1. Create User A: `user-a@test.com`
2. Log food for User A
3. Logout
4. Create User B: `user-b@test.com`
5. Log food for User B
6. Check: User B doesn't see User A's data
7. Login as User A again
8. Check: User A still sees their own data

- ✅ Each user sees only their data
- ✅ Separate JSON files created in data/ directory

### 8. Stripe Payment Tests

**Test Case 1: Checkout Session Creation**
- ✅ Login as user
- ✅ Go to /pricing
- ✅ Click "Start Free Trial" or subscribe button
- ✅ Creates Stripe checkout session
- ✅ Redirects to Stripe checkout page

**Test Case 2: Successful Payment**
- ✅ On Stripe checkout, enter test card: `4242 4242 4242 4242`
- ✅ Expiry: 12/25
- ✅ CVC: 123
- ✅ ZIP: 12345
- ✅ Complete payment
- ✅ Redirects to /payment-success
- ✅ Dashboard shows "Active" subscription

**Test Case 3: Payment Cancellation**
- ✅ Start checkout
- ✅ Click "Back" or close window
- ✅ Redirects to /pricing
- ✅ User remains on trial

**Test Case 4: Webhook Processing**
- ✅ Check Stripe dashboard for webhook events
- ✅ Verify `checkout.session.completed` received
- ✅ Check data/users.json - subscription status updated

### 9. Subscription Expiry Tests

**Test Case 1: Trial Expired**
1. Edit data/users.json
2. Set trial_end to past date
3. Set subscription_status to "trial"
4. Try accessing /dashboard
5. Should redirect to /subscription-expired

- ✅ Expired trial blocks access
- ✅ Subscription page shows subscribe button
- ✅ Can subscribe to reactivate

**Test Case 2: Active Subscription**
1. Set subscription_status to "active"
2. Access /dashboard
- ✅ Dashboard accessible
- ✅ No trial banner

### 10. Security Tests

**Test Case 1: Protected Routes**
- ✅ Visit /dashboard while logged out → redirects to /login
- ✅ Visit /api/stats while logged out → returns 401
- ✅ Try accessing another user's data → blocked

**Test Case 2: Session Management**
- ✅ Login, close browser, reopen → still logged in
- ✅ Logout → session cleared
- ✅ Can't access dashboard after logout

### 11. Deployment Tests

**After deploying to Railway/Heroku:**

**Test Case 1: Production Environment**
- ✅ App accessible at production URL
- ✅ HTTPS enabled
- ✅ All pages load
- ✅ Environment variables set correctly

**Test Case 2: Stripe Integration**
- ✅ Signup works on production
- ✅ Payment flow works with test card
- ✅ Webhook receives events
- ✅ Subscription status updates

**Test Case 3: Data Persistence**
- ✅ Create account on production
- ✅ Log data
- ✅ Logout and login again
- ✅ Data persists

### 12. Mobile/Responsive Tests

Test on different screen sizes:
- ✅ iPhone (375px)
- ✅ iPad (768px)
- ✅ Desktop (1920px)

All pages should:
- ✅ Display correctly
- ✅ Forms work
- ✅ Charts resize properly
- ✅ Navigation accessible

### 13. Browser Compatibility

Test in:
- ✅ Chrome
- ✅ Safari
- ✅ Firefox
- ✅ Edge

All features should work in all browsers.

## Pre-Launch Checklist

Before going live:

- [ ] All tests pass
- [ ] Stripe test mode working
- [ ] Webhooks configured and tested
- [ ] Environment variables set
- [ ] HTTPS enabled
- [ ] Error pages created (404, 500)
- [ ] Privacy policy added (if required)
- [ ] Terms of service added (if required)
- [ ] Contact/support email set up
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Launch materials ready (Reddit post, tweets)

## Going Live Checklist

- [ ] Switch Stripe to live mode
- [ ] Update Stripe keys to live keys
- [ ] Set up live webhook
- [ ] Test live payment flow with real card (refund after)
- [ ] Monitor error logs
- [ ] Test signup → payment → usage flow
- [ ] Ready to launch! 🚀

## Monitoring After Launch

Daily checks:
- [ ] Check error logs
- [ ] Monitor Stripe dashboard for payments
- [ ] Check webhook delivery
- [ ] Monitor user signups
- [ ] Respond to support emails

## Rollback Plan

If something goes wrong:
1. Check logs for errors
2. Fix critical bugs
3. Redeploy
4. If unfixable, take site offline temporarily
5. Communicate with users via email

---

**Test everything, launch confidently!** 🎯
