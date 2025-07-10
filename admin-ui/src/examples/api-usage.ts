// /**
//  * Examples của cách sử dụng API services trong Admin UI
//  * File này chỉ để demo, không import vào app thực tế
//  */

// import { adminApi, usersApi, organizationsApi, projectsApi } from '../api';

// // Example 1: Sử dụng combined adminApi object
// async function exampleUsingAdminApi() {
//   try {
//     // Get system stats
//     const stats = await adminApi.dashboard.getSystemStats();
//     console.log('System stats:', stats);

//     // Get all users
//     const users = await adminApi.users.getUsers({
//       page: 1,
//       page_size: 10,
//       search: 'admin@example.com'
//     });
//     console.log('Users:', users);

//     // Get all organizations
//     const orgs = await adminApi.organizations.getOrganizations({
//       status: 'active'
//     });
//     console.log('Organizations:', orgs);

//   } catch (error) {
//     console.error('API Error:', error);
//   }
// }

// // Example 2: Sử dụng individual services
// async function exampleUsingIndividualServices() {
//   try {
//     // Users operations
//     const newUser = await usersApi.createUser({
//       email: 'test@example.com',
//       name: 'Test User',
//       password: 'password123',
//       is_active: true
//     });
//     console.log('Created user:', newUser);

//     // Organizations operations
//     const newOrg = await organizationsApi.createOrganization({
//       name: 'Test Organization',
//       centicredits: 1000,
//       is_webhooks_enabled: true
//     });
//     console.log('Created organization:', newOrg);

//     // Projects operations
//     const newProject = await projectsApi.createProject({
//       name: 'Test Project',
//       description: 'A test project',
//       organization_id: newOrg.id
//     });
//     console.log('Created project:', newProject);

//   } catch (error) {
//     console.error('API Error:', error);
//   }
// }

// // Example 3: Error handling
// async function exampleErrorHandling() {
//   try {
//     const user = await usersApi.getUser('non-existent-id');
//     console.log('User:', user);
//   } catch (error: any) {
//     if (error.response?.status === 404) {
//       console.log('User not found');
//     } else if (error.response?.status === 401) {
//       console.log('Unauthorized - need to login');
//     } else {
//       console.error('Unexpected error:', error);
//     }
//   }
// }

// // Example 4: Authentication flow
// async function exampleAuthFlow() {
//   try {
//     // Login
//     const loginResult = await adminApi.auth.login({
//       email: 'admin@example.com',
//       password: 'password123'
//     });
    
//     // Token sẽ được store tự động trong localStorage
//     console.log('Login successful:', loginResult);

//     // Verify current user
//     const currentUser = await adminApi.auth.getCurrentUser();
//     console.log('Current user:', currentUser);

//     // Logout
//     await adminApi.auth.logout();
//     console.log('Logged out successfully');

//   } catch (error) {
//     console.error('Auth error:', error);
//   }
// }

// // Example 5: Pagination và filtering
// async function examplePaginationAndFiltering() {
//   try {
//     // Get bots với filtering
//     const bots = await adminApi.bots.getBots({
//       page: 1,
//       page_size: 20,
//       status: 'in_meeting',
//       platform: 'zoom',
//       search: 'weekly meeting'
//     });
    
//     console.log(`Found ${bots.total} bots, showing page ${bots.page} of ${bots.pages}`);
//     console.log('Bots:', bots.items);

//     // Get transcriptions với filtering
//     const transcriptions = await adminApi.transcriptions.getTranscriptions({
//       status: 'completed',
//       provider: 'deepgram',
//       page: 1,
//       page_size: 50
//     });
    
//     console.log('Completed transcriptions:', transcriptions);

//   } catch (error) {
//     console.error('Error:', error);
//   }
// }

// // Example 6: Real-time operations
// async function exampleRealTimeOperations() {
//   try {
//     // Get bot real-time status
//     const botStatus = await adminApi.bots.getBotStatus('bot-123');
//     console.log('Bot status:', botStatus);

//     // Send command to bot
//     const commandResult = await adminApi.bots.sendCommand('bot-123', {
//       type: 'mute'
//     });
//     console.log('Command result:', commandResult);

//     // Get queue status
//     const queueStatus = await adminApi.transcriptions.getQueueStatus();
//     console.log('Queue status:', queueStatus);

//   } catch (error) {
//     console.error('Error:', error);
//   }
// }

// // Export examples (không chạy tự động)
// export {
//   exampleUsingAdminApi,
//   exampleUsingIndividualServices,
//   exampleErrorHandling,
//   exampleAuthFlow,
//   examplePaginationAndFiltering,
//   exampleRealTimeOperations
// }; 