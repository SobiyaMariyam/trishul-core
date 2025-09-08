// Unified API exports for easy backend integration
// In Phase 3, simply change these imports to point to real API endpoints

import { kavachApi } from "./kavach";
import { rudraApi } from "./rudra";
import { trinetraApi } from "./trinetra";

export { kavachApi, rudraApi, trinetraApi };

// Future: Replace with real API client
// export { kavachApi } from "./backend/kavach";
// export { rudraApi } from "./backend/rudra";
// export { trinetraApi } from "./backend/trinetra";

// Default export for convenience
const Api = {
  kavach: kavachApi,
  rudra: rudraApi,
  trinetra: trinetraApi,
};

export default Api;
