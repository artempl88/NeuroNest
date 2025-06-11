export const CONFIG = {
  API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  PAYMENT_ADDRESS: process.env.NEXT_PUBLIC_PAYMENT_ADDRESS || 'EQBfbkxNqgzQQm_GqL4zQGLm2N6_r-5rG_3k4l__NF8qf',
  COLLECTION_ADDRESS: 'EQCGbQyAJxxMsYQWLCklkXQq4fkIBK3kz3GA1TkFJyUR9nTH',
  
  // Timeouts
  NFT_CHECK_DELAY: 1000,
  TRANSACTION_TIMEOUT: 60,
  
  // URLs
  BRIDGE_URL: 'https://bridge.tonapi.io',
  GETGEMS_URL: 'https://getgems.io/collection/EQCGbQyAJxxMsYQWLCklkXQq4fkIBK3kz3GA1TkFJyUR9nTH',
  
  // Access levels
  ACCESS_LEVELS: {
    BASIC_MIN: 1,
    ADVANCED_MIN: 3,
    PREMIUM_MIN: 10
  }
} 