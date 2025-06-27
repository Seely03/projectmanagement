# Transitioning from Local to Cognito Authentication

This guide explains how to transition from the built-in local authentication to AWS Cognito authentication in the Project Manager application.

## Why Transition to Cognito?

Amazon Cognito provides several advantages over local authentication:

1. **Enhanced Security**: Professional-grade authentication with features like MFA, phone verification, and more.
2. **Reduced Maintenance**: No need to maintain password reset flows, account verification, etc.
3. **Social Identity Federation**: Allow users to sign in with Google, Facebook, Amazon, or other identity providers.
4. **Scalability**: Handles user management at scale without additional work.
5. **Compliance**: Helps meet security and compliance requirements.

## Preparing for the Transition

### 1. Set Up Cognito Resources

Follow the guide in `docs/cognito-integration.md` to set up the required AWS Cognito resources.

### 2. Update Environment Variables

1. Create a `.env` file based on the `.env.example` template
2. Set `USE_COGNITO_AUTH=false` during development
3. Update all the Cognito-related environment variables with your values

### 3. Create a Migration Strategy for Existing Users

For existing users in your local database, you have several options:

#### Option A: Pre-create Users in Cognito (Recommended for small user bases)

1. Export a list of existing users from your database
2. Use the AWS CLI or Console to create these users in Cognito
3. Send users a password reset email to set their Cognito password

Example AWS CLI command to create a user:
```bash
aws cognito-idp admin-create-user \
  --user-pool-id YOUR_USER_POOL_ID \
  --username username \
  --user-attributes Name=email,Value=user@example.com Name=email_verified,Value=true \
  --temporary-password Temp123! \
  --message-action SUPPRESS
```

#### Option B: Gradual Migration (Better for larger user bases)

1. Keep both authentication systems running side by side
2. When users log in with local auth, create a corresponding Cognito user
3. Gradually transition all users as they log in

## Making the Switch

### 1. Testing the Integration

Before fully switching to Cognito, test the integration thoroughly:

1. Set `USE_COGNITO_AUTH=true` in your development environment
2. Test logging in with test Cognito users
3. Verify that all user-related functions still work correctly

### 2. Deploy the Changes

1. Update your production environment variables to use Cognito
2. Deploy the application to your production environment
3. Monitor the logs for any authentication-related issues

### 3. Clean Up (After Successful Migration)

Once all users have been successfully migrated to Cognito:

1. Backup the local user data for records
2. Update the database schema to remove password fields if no longer needed
3. Remove the local authentication code (optional)

## Handling Edge Cases

### Users with the Same Email in Both Systems

If a user exists in both your local database and Cognito with the same email:

1. Identify these users before the migration
2. Merge their data in your application database
3. Ensure their Cognito account has the correct attributes

### Admin Users

For admin users who require special privileges:

1. Add a custom attribute in Cognito for admin status, or
2. Keep the admin flag in your local database and link users by email

### Failed Migrations

If a user fails to migrate properly:

1. Implement a fallback to local authentication
2. Provide a manual process for support staff to assist users

## Rollback Plan

If you need to roll back to local authentication:

1. Set `USE_COGNITO_AUTH=false` in your environment
2. Ensure all local authentication routes are still functional
3. Communicate with users about the authentication change

## Monitoring and Support

After the transition:

1. Monitor failed login attempts to identify potential issues
2. Provide clear documentation for users about the new login process
3. Set up a support process for users who have trouble logging in 